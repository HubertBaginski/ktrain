from ..imports import *
from subprocess import Popen, PIPE, DEVNULL



def extract_copy(corpus_path, output_path):
    """
    Crawl <corpus_path>, extract or read plain text from application/pdf
    and text/plain files and then copy them to output_path.
    Args:
        corpus_path(str):  root folder containing documents
        output_path(str):  root folder of output directory
    Returns:
        list: list of skipped filenames
    """
    skipped = set()
    num_skipped = 0
    corpus_path = os.path.normpath(corpus_path)
    output_path = os.path.normpath(output_path)
    for idx, filename in enumerate(extract_filenames(corpus_path)):
        if idx %1000 == 0: print('processed %s doc(s)' % (idx+1))
        mtype = get_mimetype(filename)
        if mtype == 'application/pdf':
            text = pdftotext(filename)
            text = text.strip()
        elif mtype and mtype.split('/')[0] == 'text':
            with open(filename, 'r') as f:
                text = f.read()
                text = str.encode(text)
        else:
            num_skipped += 1
            if not mtype:
                mtype =  os.path.splitext(filename)[1]
                if not mtype: mtype == 'unknown'
            skipped.add(mtype)
            continue
        if not text: 
            num_skipped += 1
            continue
        fpath, fname = os.path.split(filename)
        if mtype == 'application/pdf': fname = fname+'.txt'
        relfpath = fpath.replace(corpus_path, '')
        relfpath = relfpath[1:] if relfpath and relfpath[0] == os.sep else relfpath
        opath = os.path.join(output_path, relfpath)
        if not os.path.exists(opath):
            os.makedirs(opath)
        ofilename = os.path.join(opath, fname)
        with open(ofilename, 'wb') as f:
            f.write(text)
    print('processed %s docs' % (idx+1))
    print('done.')
    print('skipped %s docs' % (num_skipped))
    if skipped: print('%s' %(skipped))


def get_mimetype(filepath):
    return mimetypes.guess_type(filepath)[0]

def is_txt(filepath):
    return mimetypes.guess_type(filepath)[0] == 'text/plain'

def is_pdf(filepath):
    return mimetypes.guess_type(filepath)[0] == 'application/pdf'



def pdftotext(filename):
    """
    Use pdftotext program to convert PDF to text string.
    :param filename: of PDF file
    :return: text from file, or empty string if failure
    """
    output = Popen(['pdftotext', '-q', filename, '-'],
                   stdout=PIPE).communicate()[0]
    # None may indicate damage, but convert for consistency
    return '' if output is None else output



def requires_ocr(filename):
    """
    Uses pdffonts program to determine if the PDF requires OCR, i.e., it
    doesn't contain any fonts.
    :param filename: of PDF file
    :return: True if requires OCR, False if not
    """
    output = Popen(['pdffonts', filename], stdout=PIPE,
                   stderr=DEVNULL).communicate()[0]
    return len(output.split('\n')) < 4


def extract_filenames(corpus_path, follow_links=False):
    if os.listdir(corpus_path) == []:
        raise ValueError("%s: path is empty" % corpus_path)
    walk = os.walk
    for root, dirs, filenames in walk(corpus_path, followlinks=follow_links):
        for filename in filenames:
            try:
                yield os.path.join(root, filename)
            except:
                continue

