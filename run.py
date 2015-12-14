from time import sleep, strftime
from hkz.third_update import third_update

if __name__ == '__main__':
    while 1:
        if strftime('%H%M') not in ['0130', '0330', '0700', '0930', '1515']:
            print strftime('%Y-%m-%d %H:%M:%S %A')
            sleep(20.0)
        else:
            try:
                third_update()
            except:
                pass
    # third_update()
