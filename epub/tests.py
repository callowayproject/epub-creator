from django.conf import settings
from django.test import TestCase
from epub.models import EPub, EPubMetadata, format_name
from simplestory.models import Story



class TestEPub(TestCase):
    fixtures = ['stories.json']
    
    def testPubGeneration(self):
        import os, subprocess
        img_path = os.path.abspath(os.path.join(settings.APP,'example','simplestory','fixtures','dailytimes.svg'))
        final_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'testpub.epub'))
        epubcheck = os.path.abspath(os.path.join(os.path.dirname(__file__),'bin','epubcheck-1.0.3','epubcheck-1.0.3.jar'))
        e = EPub()
        e.metadata.title="A Good Day to Enjoy"
        e.metadata.publisher = "Daily Times Publishing Inc"
        e.metadata.language = 'en-US'
        e.metadata.add_date('2009-07-05')
        e.metadata.add_date('2009-07-06', event="publication")
        e.metadata.modification_date = '2009-08-08'
        e.metadata.add_subject("Zombies")
        e.metadata.add_subject("Apocolypse")
        e.metadata.add_subject("Teen Angst")
        e.metadata.add_relation("Uncle")
        e.metadata.add_relation("Grandmother")
        e.metadata.add_meta('price', 'USD 9.99')
        
        e.add_image(img_path, 'logo.svg')
        s = Story.objects.all()
        for item in s:
            e.add_article(item.headline, item, item.slug+".html", item.byline.replace("by ", ""))
        
        e.generate_epub(final_path)
        
        retcode = subprocess.Popen(['java -jar %s %s' % (epubcheck,final_path),], 
                        shell=True, executable='/bin/bash', env=os.environ,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if retcode[1]:
            print retcode[1]
            raise Exception("epub is not valid.")

class TestNameParsing(TestCase):
    def testNameParsing(self):
        test_data = (
            ('Charles Henry Pearson', 'Pearson, Charles Henry'),
            ('Charles H. Pearson', 'Pearson, Charles H'),
            ('Charles H. Pearson, Jr.', 'Pearson Jr, Charles H'),
            ('Charles H. St. James, Jr.', 'St James Jr, Charles H'),
            ('Mary Kate L Van Hinder, Jr.', 'Van Hinder Jr, Mary Kate L')
        )
        
        for testval, answer in test_data:
            self.assertEquals(format_name(testval), answer)
    
    def testMetadata(self):
        results = u'<dc:publisher>Daily Times Publishing Inc</dc:publisher>\n<dc:language>en-US</dc:language>\n<dc:creator opf:file-as="Oordt, Corey J" opf:role="aut">Corey J Oordt</dc:creator>\n<dc:title>A Good Day to Enjoy</dc:title>\n<dc:date >2009-07-05</dc:date>\n<dc:relation>Uncle</dc:relation>\n<dc:relation>Grandmother</dc:relation>\n<dc:identifier opf:scheme="uuid" id="BookId">81ca5fdd-4546-42dd-8b81-86ad52d4c271</dc:identifier>\n<dc:subject>Zombies</dc:subject>\n<dc:subject>Apocolypse</dc:subject>\n<dc:subject>Teen Angst</dc:subject>'
        
        md = EPubMetadata()
        md.set_unique_id(value='81ca5fdd-4546-42dd-8b81-86ad52d4c271', id='BookId', scheme='uuid')
        md.add_creator("Corey J Oordt")
        md.title="A Good Day to Enjoy"
        md.publisher = "Daily Times Publishing Inc"
        md.language = 'en-US'
        md.add_date('2009-07-05')
        md.add_subject("Zombies")
        md.add_subject("Apocolypse")
        md.add_subject("Teen Angst")
        md.add_relation("Uncle")
        md.add_relation("Grandmother")
        self.assertEquals(unicode(md), results)