import threading
import sys
sys.path.append(r'E:\netval_auto_v2.0')
from modules.file_to_database.file_to_database import *
from modules.netvalues_base.netvalues_base import *
from modules.netvalues_calculation.netval_calculation import *
from products_info.global_vars import *
from products_info.products_info import *


if __name__ == '__main__':

    # 更新估值表 至 数据库 采用多线程加速更新 须确保各个产品所在的线程更新完成后再开始计算该产品的净值
    update_treads = []
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        filedir = os.path.join(filedir_base,''.join(['估值信息 ',p['pname']]))
        processor = rawfile_process(dbdir=dbdir,filedir=filedir,pcode=p['pcode'],pname=p['pname'])
        #processor.update_database(VARTYPES)
        t = threading.Thread(target=processor.update_database,args=(VARTYPES,))
        update_treads.append(t)
    for t in update_treads:
        t.start()
    for t in update_treads:
        t.join()
    del update_treads
    print('rawfile update finished')
    print('')
    print('')

    # 提取估值表基础元素
    base_treads = []
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        elements_extracter = netvalues_base(dbdir,netdbdir)
        #elements_extracter.update_netdb(codedict=CODEDICT[p['nickname']],indexmark='科目代码',valcols=('市值','市值本币'))
        t = threading.Thread(target=elements_extracter.update_netdb,args=(CODEDICT[p['nickname']],'科目代码',('市值','市值本币')))
        base_treads.append(t)
    for t in base_treads:
        t.start()
    for t in base_treads:
        t.join()
    del base_treads
    print('netval base update finished')
    print('')
    print('')

    # 计算净值
    calc_treads = []
    for k in PRODUCTS_INFO:
        if k == '烜鼎鑫诚九号':
            earnvars = ['earnAl','earnT']
            continue  # 目前估值表不全
        else:
            earnvars = ['earn']
        p = PRODUCTS_INFO[k]
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        calculator = netvalues_calculation(pname=p['pname'],netdbdir=netdbdir,confirmdays=p['confirmdays'],precision=p['precision'])
        calculator.generate_netvalues(earnvars = earnvars)
    #     t = threading.Thread(target=calculator.generate_netvalues,args=(earnvars,))
    #     calc_treads.append(t)
    # for t in calc_treads:
    #     t.start()
    # for t in calc_treads:
    #     t.join()
    # del calc_treads
    print('netval calc update finished')
    print('')
    print('')