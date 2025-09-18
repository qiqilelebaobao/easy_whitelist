import logging
from enum import Enum, auto
from typing import Optional

from .template import list_template, set_template

class CommandAction(Enum):
    CONTINUE = auto()
    BREAK = auto()
    NOTHING = auto()


CMD_LIST = 'l'
CMD_EMPTY = ''
CMD_CREATE = 'c'
CMD_EXIT = 'q'
INPUT_PROMPT = 'Please choose # template to set (or [L]ist, [C]reate, [Q]uit): '


def _handle_digit_input(user_input: str, common_client, template_ids: list, proxy: Optional[str]) -> None:
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
        logging.warning("Invalid number: %s. Please enter a number between 1 and %d",
                        user_input, len(template_ids))


def _handle_command_input(user_input: str, common_client, template_ids: list, proxy: Optional[str]) -> CommandAction:
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
        CMD_LIST: (lambda: list_template(common_client), CommandAction.CONTINUE),
        CMD_EMPTY: (lambda: None, CommandAction.CONTINUE),
        CMD_CREATE: (lambda: None, CommandAction.CONTINUE),
        CMD_EXIT: (lambda: None, CommandAction.BREAK),
        # 'c': lambda: create_template(common_client, proxy) # 假设有create_template函数
        # 可轻松扩展其他命令，例如 'h': show_help
    }

    if user_input in command_handlers:
        handler, action = command_handlers[user_input]
        handler()
        return action
    else:
        logging.warning(
            f"Invalid command: {user_input}. Available commands: l, c, q")
        return CommandAction.CONTINUE


def loop_list(common_client, proxy: Optional[str] = None) -> None:
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
