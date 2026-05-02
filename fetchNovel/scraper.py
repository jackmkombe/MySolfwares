import requests
from bs4 import BeautifulSoup
import os
import re
import time
import random
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from deep_translator import GoogleTranslator

class NovelScraper:
    def __init__(self, base_url, selector, batch_size, output_dir="downloads", delay=2, translate=False, update_log_callback=print):
        self.base_url = base_url
        self.selector = selector
        self.batch_size = batch_size
        self.output_dir = output_dir
        self.delay = delay # Average delay in seconds
        self.translate = translate
        self.update_log = update_log_callback
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
        self.current_chapter_url = base_url
        self.last_successful_url = base_url # To use as Referer
        self.chapters_in_current_batch = []
        self.batch_count = 1
        self.stop_requested = False

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_headers(self, referer=None):
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive"
        }
        if referer:
            headers["Referer"] = referer
        else:
            headers["Referer"] = "https://www.google.com/"
        return headers

    def get_next_url(self, url):
        # Try to find the chapter number in the URL and increment it
        # Patterns like /1 or /chapter-1
        match = re.search(r'(\d+)(?=[^/]*$)', url)
        if match:
            num = int(match.group(1))
            new_num = num + 1
            # Replace only the last occurrence
            return url[:match.start()] + str(new_num) + url[match.end():]
        return None

    def translate_text(self, text):
        if not text or not self.translate:
            return text
        
        try:
            translator = GoogleTranslator(source='auto', target='fr')
            # Google Translate limit is approx 5000 chars per request
            # We split by paragraphs to be safe
            paragraphs = text.split('\n')
            translated_paragraphs = []
            
            current_chunk = ""
            for p in paragraphs:
                if len(current_chunk) + len(p) + 1 < 4500:
                    current_chunk += p + "\n"
                else:
                    if current_chunk.strip():
                        translated_paragraphs.append(translator.translate(current_chunk))
                    current_chunk = p + "\n"
            
            if current_chunk.strip():
                translated_paragraphs.append(translator.translate(current_chunk))
                
            return "\n".join(translated_paragraphs)
        except Exception as e:
            self.update_log(f"Translation error: {e}")
            return text # Return original if translation fails

    def parse_selector(self, selector_str):
        """Parse CSS selector into components with support for multiple patterns"""
        if not selector_str:
            return []
        
        patterns = []
        # Split by comma for multiple selectors
        for selector in selector_str.split(','):
            selector = selector.strip()
            if selector:
                patterns.append(selector)
        return patterns
    
    def find_content_by_selector(self, soup, selector_patterns):
        """Find content using multiple selector strategies"""
        import re
        
        for pattern in selector_patterns:
            try:
                element = None
                
                # CSS selector parsing
                if pattern.startswith('#'):
                    # ID selector
                    element = soup.find(id=pattern[1:])
                elif pattern.startswith('.'):
                    # Class selector - handle multiple classes
                    classes = pattern[1:].split('.')
                    element = soup.find(class_=lambda x: x and all(cls in x for cls in classes))
                elif '[' in pattern and ']' in pattern:
                    # Attribute selector like [aria-label="content"]
                    attr_match = re.search(r'\[([^=]+)(?:="([^"]+)")?\]', pattern)
                    if attr_match:
                        attr_name = attr_match.group(1)
                        attr_value = attr_match.group(2)
                        if attr_value:
                            element = soup.find(attrs={attr_name: attr_value})
                        else:
                            element = soup.find(attrs={attr_name: True})
                else:
                    # Try as tag name or direct ID/class
                    element = soup.find(id=pattern) or soup.find(class_=pattern) or soup.find(pattern)
                
                if element:
                    return element
                    
            except Exception as e:
                self.update_log(f"Selector pattern '{pattern}' failed: {e}")
                continue
        
        return None
    
    def find_content_fallback(self, soup):
        """Fallback strategies to find novel content"""
        candidates = []
        
        # Strategy 1: Common content containers
        common_selectors = [
            '#readcontent', '.readcontent', '#content', '.content',
            '.post-content', '.entry-content', '.article-content',
            '.td-post-content', '.tdb-single-content', '.single-content',
            '[aria-label*="content"]', '[role="main"]',
            '.tdb-block-inner', '.td-fix-index'
        ]
        
        for selector in common_selectors:
            element = self.find_content_by_selector(soup, [selector])
            if element:
                text_length = len(element.get_text().strip())
                if text_length > 200:  # Reasonable content length
                    candidates.append((element, text_length))
        
        # Strategy 2: Find divs with large text content
        for div in soup.find_all('div'):
            text = div.get_text().strip()
            if len(text) > 500:  # Substantial content
                # Check if it looks like novel content (has paragraphs)
                paragraphs = div.find_all('p')
                if len(paragraphs) >= 2 or '\n\n' in text:
                    candidates.append((div, len(text)))
        
        # Strategy 3: Look for elements with novel-related keywords
        novel_keywords = ['chapter', 'chap', 'novel', 'story', 'read']
        for element in soup.find_all(['div', 'article', 'section']):
            classes = ' '.join(element.get('class', []))
            id_attr = element.get('id', '')
            aria_label = element.get('aria-label', '')
            
            combined_text = f"{classes} {id_attr} {aria_label}".lower()
            if any(keyword in combined_text for keyword in novel_keywords):
                text_length = len(element.get_text().strip())
                if text_length > 300:
                    candidates.append((element, text_length))
        
        # Return the candidate with most content
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None

    def fetch_chapter(self, url):
        try:
            # Stealth: Random delay
            sleep_time = random.uniform(self.delay * 0.5, self.delay * 1.5)
            time.sleep(sleep_time)

            # 1. Fetch
            content_found = False
            for attempt in range(2):
                try:
                    response = requests.get(url, headers=self.get_headers(referer=self.last_successful_url), timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # 3. Find Content with robust selector
                    content_div = None
                    selector_patterns = self.parse_selector(self.selector)
                    
                    # Try user-provided selectors first
                    if selector_patterns:
                        content_div = self.find_content_by_selector(soup, selector_patterns)
                    
                    # Fallback to automatic detection
                    if not content_div:
                        content_div = self.find_content_fallback(soup)
                    
                    if content_div:
                        content_found = True
                        self.update_log(f"✓ Found content using selector: {content_div.get('id', content_div.get('class', 'unknown'))}")
                        break
                except Exception as e:
                    if attempt == 0:
                        self.update_log(f"⚠️ Problème sur {url} (tentative 1): {str(e)[:50]}...")
                        time.sleep(2)
                        continue
                
            if not content_found:
                self.update_log(f"❌ Contenu introuvable pour {url} après essais.")
                return None, None

            # 4. Title
            title = "Unknown Chapter"
            try:
                title_elem = content_div.find("h1")
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    title = f"Chapter {url.split('/')[-1]}"
            except Exception as e:
                self.update_log(f"Title Error: {e}")

            # 5. Clean & Extract Text
            try:
                txt_wrap = content_div.find(class_="txtwrap") or content_div
                
                # Super safe cleaning
                for tag in txt_wrap.find_all(True): # find ALL tags
                    if not tag: continue
                    
                    try:
                        # Extract tag id safely
                        tag_id = getattr(tag, 'get', lambda x: None)('id')
                        tag_name = getattr(tag, 'name', '')
                        
                        if tag_id in ['reportErrorBtn', 'reportToolTip']:
                            tag.decompose()
                        elif tag_name in ['script', 'ins', 'style', 'iframe', 'button']:
                            tag.decompose()
                    except:
                        pass

                # Handle line breaks
                for br in txt_wrap.find_all("br"):
                    if br:
                        br.replace_with("\n\n")
                
                text = txt_wrap.get_text()
                if not text or not text.strip():
                    return title, "No content found."

                # Cleanup whitespace
                text = re.sub(r'[ \t]+', ' ', text)
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = text.strip()
                
                if self.translate:
                    self.update_log(f"Translating chapter...")
                    text = self.translate_text(text)
                    title = self.translate_text(title)
                
                return title, text
            except Exception as e:
                self.update_log(f"Text Extraction Error on {url}: {e}")
                import traceback
                self.update_log(traceback.format_exc())
                return title, "Error extracting text."

        except Exception as e:
            self.update_log(f"Unexpected error on {url}: {e}")
            return None, None

    def save_batch(self):
        if not self.chapters_in_current_batch:
            return

        # Extract novel name and chapter numbers for a clean filename
        # Example: "Douluo Dalu 4 - Ultimate Fighting c1 - c200"
        
        def extract_chapter_num(title):
            nums = re.findall(r'\d+', title)
            return nums[-1] if nums else "0"

        # Try to extract a clean "Novel Name" from first chapter title if possible
        # or use a default if it's just "Chapter 1"
        first_title = self.chapters_in_current_batch[0][0]
        last_title = self.chapters_in_current_batch[-1][0]
        
        start_num = extract_chapter_num(first_title)
        end_num = extract_chapter_num(last_title)
        
        # Clean novel name: remove "Chapter X", "Capitulo X", etc.
        novel_name = re.sub(r'(?i)chapter\s*\d+.*|capitulo\s*\d+.*', '', first_title).strip()
        if not novel_name or novel_name == first_title:
            # Fallback to a part of the URL or a generic name if title is just "Chapter 1"
            novel_name = self.base_url.split('/')[-2].replace('-', ' ').title()

        filename_base = f"{novel_name} c{start_num} - c{end_num}"
        # Final safety cleanup for filename characters
        filename_base = re.sub(r'[\\/*?:"<>|]', "", filename_base).strip()
        
        docx_path = os.path.join(self.output_dir, f"{filename_base}.docx")
        pdf_path = os.path.join(self.output_dir, f"{filename_base}.pdf")

        # --- SAVE DOCX ---
        doc = Document()
        
        # Define Character and Paragraph styles for a "Book" look
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        
        # Set default paragraph format
        paragraph_format = style.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph_format.first_line_indent = Inches(0.3)
        paragraph_format.line_spacing = 1.15
        paragraph_format.space_after = Pt(12)

        for title, content in self.chapters_in_current_batch:
            # Chapter Title
            h = doc.add_heading(title, level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            # Reset title formatting if needed (Headings often use sans-serif)
            run = h.runs[0]
            run.font.name = 'Times New Roman'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
            
            # Chapter Content
            # Novel content often has multiple paragraphs. Split by double newline if present, or single.
            # We try to maintain the original structure.
            paragraphs = content.split('\n')
            for p_text in paragraphs:
                if p_text.strip():
                    p = doc.add_paragraph(p_text.strip())
            
            doc.add_page_break()
            
        doc.save(docx_path)
        self.update_log(f"Saved DOCX: {docx_path}")

        # --- SAVE PDF ---
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
        styles = getSampleStyleSheet()
        
        # Custom style for Novel Body
        style_novel_body = ParagraphStyle(
            'NovelBody',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            firstLineIndent=20,
            spaceAfter=10
        )
        
        # Custom style for Novel Title
        style_novel_title = ParagraphStyle(
            'NovelTitle',
            parent=styles['Heading1'],
            fontName='Times-Bold',
            fontSize=13,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        )

        story = []
        from reportlab.platypus import PageBreak
        
        for title, content in self.chapters_in_current_batch:
            story.append(Paragraph(title, style_novel_title))
            
            # Split content into paragraphs for PDF
            paragraphs = content.split('\n')
            for p_text in paragraphs:
                if p_text.strip():
                    # Clean up some common web-novel artifacts or double spaces if any
                    clean_text = p_text.strip().replace('  ', ' ')
                    try:
                        story.append(Paragraph(clean_text, style_novel_body))
                    except:
                        # Fallback for very long single lines or characters reportlab might dislike
                        story.append(Paragraph("Chapter text part...", style_novel_body))
            
            story.append(PageBreak())
        
        doc_pdf = SimpleDocTemplate(pdf_path, pagesize=letter, 
                                   rightMargin=40, leftMargin=40, 
                                   topMargin=40, bottomMargin=40)
        doc_pdf.build(story)
        self.update_log(f"Saved PDF: {pdf_path}")

        self.chapters_in_current_batch = []
        self.batch_count += 1

    def run(self, total_chapters):
        self.update_log(f"Starting fetch for {total_chapters} chapters...")
        
        count = 0
        current_url = self.base_url
        
        while count < total_chapters and not self.stop_requested:
            self.update_log(f"Fetching Chapter {count + 1} from {current_url}...")
            title, content = self.fetch_chapter(current_url)
            
            if title and content:
                self.chapters_in_current_batch.append((title, content))
                count += 1
                self.last_successful_url = current_url
                
                if count % self.batch_size == 0:
                    self.save_batch()
                
                next_url = self.get_next_url(current_url)
                if not next_url:
                    self.update_log("Could not determine next URL. Stopping.")
                    break
                current_url = next_url
            else:
                self.update_log("Failed to fetch chapter content. Stopping.")
                break
        
        # Save remaining
        if self.chapters_in_current_batch:
            self.save_batch()
        
        self.update_log("Job Finished.")

    def stop(self):
        self.stop_requested = True
