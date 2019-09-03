import hashlib

from skimage import data as sk_data
from tkinter.filedialog import askopenfilename
import logging
import tkinter
import threading
import time
import os

from .sqlite_model import ImageTemplate
from .sqlite_orm import GetData
from .set_logger import set_logger

os.chdir(os.getcwd())
logger = set_logger()
db = GetData(logger)


def template_names_in_db():
    m = db.get(model_name='ImageTemplate', key_list=['template_type'])
    names = {x.template_type for x in m}
    return names


def _hash_str(data):
    md5 = hashlib.md5()
    md5.update(str(data).encode('utf-8'))
    return md5.hexdigest()


def auto_save(name, f_path, threshold=None):
    all_path = os.path.join(os.getcwd(), f_path)
    sk_array = sk_data.load(f=all_path, as_gray=True)
    sk_array_str = str(sk_array.tolist())
    threshold = 80 if threshold is None else threshold
    db.delete_data(model_name='ImageTemplate', filter_dic={'template_type': name})
    add_d = {'template_type': name, 'data': sk_array_str, 'threshold': threshold, 'status': 1}
    db.add(model=ImageTemplate, add_dic=add_d)


def manual_save():
    fn = askopenfilename(
        title='水印模板文件', filetypes=[
            ('jpg格式', '.jpg'), ('jpeg格式', '.jpeg'), ('png格式', '.png')])

    if fn:
        template_img = fn
        template_name = input('输入模板名字(template_type): ')
        status = input('输入状态码(status), 默认0: ')
        threshold = input('输入此模板的阈值(默认80): ')
        threshold = 80 if not threshold.strip().isdigit() else int(threshold.strip())
        if not status:
            status = 0
        go_to = input('直接入库按回车，复制到剪切板则输入c，取消输入q： ')
        if go_to not in {'q', 'Q'}:
            base_path = os.getcwd()
            all_path = os.path.join(base_path, template_img)
            sk_array = sk_data.load(f=all_path, as_gray=True)
            sk_array_str = str(sk_array.tolist())
            db_hash_data = db.get(model_name='', key_list=['hash_str'])
            db_hashes = {x.hash_str for x in db_hash_data}

            hash_data = _hash_str(sk_array_str)
            if hash_data not in db_hashes:
                try:
                    if not go_to:
                        db.add(model=ImageTemplate,
                               add_dic={'hash_data': hash_data,
                                        'template_type': template_name,
                                        'data': sk_array_str,
                                        'threshold': threshold,
                                        'status': status})

                    root = tkinter.Tk()
                    root.geometry("800x200+150+100")
                    vtext = tkinter.StringVar()
                    vtext.set(value='0')
                    lb0 = tkinter.Label(root,
                                        height=4
                                        )
                    lb0.pack(side=tkinter.TOP)
                    lb1 = tkinter.Label(root,
                                        text='已复制结果到剪切板，直接去文件下粘贴即可（20s后自动关闭）',
                                        justify=tkinter.CENTER,
                                        font=("Arial", 20))
                    lb1.pack(side=tkinter.TOP)

                    def run(run_time):
                        for i in range(1, run_time + 1):
                            # print(i)
                            txt = '已复制到剪贴板（{}s后自动关闭）'.format(str(run_time - i))
                            if not go_to:
                                txt = '已插入到数据库（{}s后自动关闭）'.format(str(run_time - i))
                            lb1['text'] = txt
                            time.sleep(1)
                        os._exit(0)

                    run_time = 30
                    if not go_to:
                        run_time = 3
                    t = threading.Thread(target=run, args=(run_time,))
                    t.setDaemon(True)
                    t.start()

                    root.clipboard_clear()
                    root.clipboard_append(str(sk_array.tolist()))
                    root.mainloop()
                    # print(sk_array.tolist())
                except Exception as E:
                    print('插入失败！')
                    logging.error('insert error! :{}'.format(E))

        else:
            print('取消操作')
            os._exit(0)
    else:
        print('取消选择')
        os._exit(0)


if __name__ == "__main__":
    manual_save()
