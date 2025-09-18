import logging

from .log.log import set_log
from .config import arg
from .tcloud import client
from .tcloud.template import list_template, set_template, create_template


INPUT_PROMPT = 'Please choose # template to set (or [L]ist, [C]reate, [Q]uit): '


def _handle_digit_input(user_input: str, common_client, template_ids: list, proxy: None | str) -> None:
    if not template_ids:
        logging.warning("No templates available. Please create one first.")
        return

    index = int(user_input)
    if 1 <= index <= len(template_ids):
        set_template(common_client, template_ids[index - 1], proxy)
    else:
        logging.warning(
            'Index out of range. Available templates: %d', len(template_ids))


def _do_nothing() -> None:
    pass


def _do_return() -> None:
    pass


def _handle_command_input(user_input: str, common_client, template_ids: list, proxy: None | str) -> bool:
    command_handlers = {
        'l': lambda: list_template(common_client),
        '': _do_nothing,
        'c': _do_nothing,
        'q': _do_return,
        # 'c': lambda: create_template(common_client, proxy) # 假设有create_template函数
        # 可轻松扩展其他命令，例如 'h': show_help
    }

    handler = command_handlers.get(user_input)
    if handler:
        handler()
        if handler == _do_return:
            return True
        else:
            return False  # 不退出循环
    else:
        logging.warning(
            'Invalid command: %s. Available commands: l, c, q', user_input)
        return False  # 不退出循环


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
                    user_input, template_ids, common_client, proxy)
            else:
                should_quit = _handle_command_input(
                    user_input, common_client, template_ids, proxy)
                if should_quit:
                    break

        except KeyboardInterrupt:
            logging.warning('\nOperation cancelled by user')
            break
        except Exception as e:
            logging.warning("\nUnexpected error occurred: %s", e)


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
