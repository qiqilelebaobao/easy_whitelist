import logging
from enum import Enum

from .log.log import set_log
from .config import arg
from .tcloud import client
from .tcloud.template import list_template, set_template, create_template


class CommandAction(Enum):
    CONTINUE = 0
    BREAK = 1
    NOTHING = 2


INPUT_PROMPT = 'Please choose # template to set (or [L]ist, [C]reate, [Q]uit): '


def _handle_digit_input(user_input: str, common_client, template_ids: list, proxy: None | str) -> None:
    """
    处理数字输入，选择模板索引

    Args:
        user_input: 用户输入的数字字符串
        common_client: 云服务客户端
        template_ids: 模板ID列表
        proxy: 代理设置，可选
    """

    if not template_ids:
        logging.warning("No templates available. Please create one first.")
        return

    try:
        index = int(user_input)
        if 1 <= index <= len(template_ids):
            set_template(common_client, template_ids[index - 1], proxy)
        else:
            logging.warning(
                'Index out of range. Available templates: %d', len(template_ids))
    except ValueError:
        logging.warning("Invalid number: %s", user_input)


def _handle_command_input(user_input: str, common_client, template_ids: list, proxy: None | str) -> CommandAction:
    """
    处理命令输入，执行相应操作

    Args:
        user_input: 用户输入的命令
        common_client: 云服务客户端
        template_ids: 模板ID列表
        proxy: 代理设置，可选

    Returns:
        CommandAction: 指示后续操作的动作
    """

    command_handlers = {
        'l': (lambda: list_template(common_client), CommandAction.CONTINUE),
        '': (lambda: None, CommandAction.CONTINUE),
        'c': (lambda: None, CommandAction.CONTINUE),
        'q': (lambda: None, CommandAction.BREAK),
        # 'c': lambda: create_template(common_client, proxy) # 假设有create_template函数
        # 可轻松扩展其他命令，例如 'h': show_help
    }

    if user_input in command_handlers:
        handler, action = command_handlers[user_input]
        handler()
        return action
    else:
        logging.warning(
            'Invalid command: %s. Available commands: l, c, q', user_input)
        return CommandAction.CONTINUE


def loop_list(common_client, proxy=None):
    template_ids = list_template(common_client)
    last_input = None

    while True:

        try:
            user_input = input(INPUT_PROMPT).strip().lower()

            if last_input == '' and user_input == '':
                break

            last_input = user_input

            if user_input.isdigit():
                _handle_digit_input(
                    user_input, common_client, template_ids, proxy)
            else:
                action = _handle_command_input(
                    user_input, common_client, template_ids, proxy)
                if action == CommandAction.BREAK:
                    break

        except KeyboardInterrupt:
            logging.warning('\nOperation cancelled by user')
            break
        except ValueError as e:
            logging.warning("Value error: %s", e)
        except ConnectionError as e:
            logging.error("Connection error: %s", e)
            break
        except Exception as e:
            logging.error("Unexpected error occurred: %s", e)
            break


def main() -> None:
    tencent, alibaba, action, target, target_id, proxy, verbose = arg.init_arg()

    set_log(verbose)

    common_client = client.get_common_client(proxy)

    cloud_provider = 'tencent' if tencent else 'aliyun'
    logging.info('Using %s cloud provider', cloud_provider.upper())

    ACTION_MAP = {
        'list': lambda: loop_list(common_client, proxy),
        'set': lambda: set_template(common_client, target_id, proxy),
        'create': lambda: create_template(common_client, target_id, proxy),
    }

    if cloud_provider == 'tencent' and target == 'template':
        if action in ACTION_MAP:
            ACTION_MAP[action]()
        else:
            logging.error('Unsupported operation: %s', action)
    else:
        logging.error("Unsupported cloud provider or target.")
