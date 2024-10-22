import argparse

def init_arg():
    '''parse parameter from command line.'''
    
    parser = argparse.ArgumentParser(prog='python3 easy.py', description='This is a cloud acl auto whitelist program.', epilog='Enjoy the tool. :) ')

    my_group = parser.add_mutually_exclusive_group(required=True)
    my_group.add_argument('-t', '-T', '--tencent', action='store_true', help='tencent cloud')
    my_group.add_argument('-a', '-A', '--alibaba', action='store_true', help='alibaba cloud')
    
    parser.add_argument('-p', '-P', '--proxy',  action='store', default=-1, type=int, help ='local HTTP proxy port')
    
    parser.add_argument('target', help='template or rule', choices=['template', 'rule'])
    parser.add_argument('action', help='list', choices=['list', 'set', 'create'])
    parser.add_argument('target_id', help='template id or rule id', nargs='?')

    args = parser.parse_args()
    
    # print(args)
    
    return args.tencent, args.alibaba, args.action, args.target, args.target_id, args.proxy
