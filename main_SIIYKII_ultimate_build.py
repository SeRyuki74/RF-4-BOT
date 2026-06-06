"""Entry point for Russian Fishing 4 Script.

Parse command line arguments and config and start running the bot.
"""

import argparse
import shlex
import sys
from pathlib import Path
from packaging.version import Version

import rich_argparse
from rich import box, print
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, utils
from rf4s.app import (
    BotApp,
    CalculateApp,
    CraftApp,
    FrictionBrakeApp,
    HarvestApp,
    MoveApp,
)

VERSION = "0.10.2"
MINIMUM_COMPATIBLE_CONFIG_VERSION = "0.8.0"
LOGO = r"""

[red]
   ________  __      __     ___  ___  __   ___   __      __        
 /"       )|" \    |" \   |"  \/"  ||/"| /  ") |" \    |" \       
(:   \___/ ||  |   ||  |   \   \  / (: |/   /  ||  |   ||  |      
 \___  \   |:  |   |:  |    \\  \/  |    __/   |:  |   |:  |      
  __/  \\  |.  |   |.  |    /   /   (// _  \   |.  |   |.  |      
 /" \   :) /\  |\  /\  |\  /   /    |: | \  \  /\  |\  /\  |\     
(_______/ (__\_|_)(__\_|_)|___/     (__|  \__)(__\_|_)(__\_|_)    
                                                                  

[/]

[bold magenta]         SIIYKII RF4 PRIVATE BUILD[/]
[bold cyan]              Bottom • Jig • Spin[/]

"""

# https://patorjk.com/software/taag/#p=testall&f=Merlin1&t=SIIYKII+&x=rainbow3&v=4&h=4&w=80&we=false

FEATURES = (
    {"name": "🎣 Auto Mancing", "command": "bot"},
    {"name": "🛠 Auto Craft", "command": "craft"},
    {"name": "🚶 Auto Jalan", "command": "move"},
    {"name": "🪱 Cari Umpan", "command": "harvest"},
    {"name": "⚙ Auto Drag", "command": "frictionbrake"},
    {"name": "📊 Kalkulator Setup", "command": "calculate"},

    {"name": "🎯 Jig Step Auto", "command": "jigstep"},
    {"name": "🐕 Walk The Dog", "command": "walkdog"},
    {"name": "🌀 Spin Auto", "command": "spinauto"},
    {"name": "🐟 Bottom Auto", "command": "bottomauto"},
    {"name": "🌊 Waky Drifting", "command": "wakydrift"},
)

BOT_BOOLEAN_ARGUMENTS = (
    ("t", "tag", "🎯 Simpan hanya ikan bertag"),
    ("c", "coffee", "☕ Minum kopi otomatis saat stamina rendah"),
    ("a", "alcohol", "🍺 Minum alkohol sebelum menyimpan ikan"),
    ("r", "refill", "🥕 Isi ulang kenyamanan & kelaparan"),
    ("H", "harvest", "🪱 Cari umpan sebelum casting"),
    ("L", "lure", "🪝 Ganti lure favorit random"),
    ("m", "mouse", "🖱 Gerakkan mouse random"),
    ("P", "pause", "⏸ Pause random sebelum lempar"),
    ("RC", "random-cast", "🎣 Lempar random tambahan"),
    ("SC", "skip-cast", "⏩ Lewati lemparan pertama"),
    ("l", "lift", "Angkat joran saat narik ikan"),
    ("e", "electro", "Aktifkan mode reel elektrik"),
    ("FB", "friction-brake", "Auto atur drag"),
    ("GR", "gear-ratio", "⚙ Ganti gear ratio otomatis"),
    ("b", "bite", "📸 Screenshot saat strike"),
    ("s", "screenshot", "🖼 Screenshot hasil tangkapan"),
    ("d", "data", "💾 Simpan data hasil mancing"),
    ("E", "email", "📧 Kirim notifikasi Email"),
    ("M", "miaotixing", "🔔 Kirim notifikasi Miaotixing"),
    ("D", "discord", "💬 Kirim notifikasi Discord"),
    ("TG", "telegram", "📱 Kirim notifikasi Telegram"),
    ("S", "shutdown", "🖥 Matikan PC setelah selesai"),
    ("SO", "signout", "🚪 Sign out setelah selesai"),
    ("BL", "broken-lure", "🪝 Auto ganti lure rusak"),
    ("SR", "spod-rod", "🎯 Auto lempar spod rod"),
    ("DM", "dry-mix", "🪣 Isi ulang dry mix"),
    ("GB", "groundbait", "💣 Isi ulang groundbait"),
    ("PVA", "pva", "📦 Isi ulang PVA"),
    ("NA", "no-animation", "⚡ Mode cepat tanpa animasi"),
)

EPILOG = """SIIYKI PRIVATE BUILD"""

# When running as an executable, use sys.executable to find the config.yaml.
# This file is not included during compilation and could not be resolved automatically
# by Nuitka.
INNER_ROOT = Path(__file__).resolve().parents[0]
if utils.is_compiled():
    OUTER_ROOT = Path(sys.executable).parent
else:
    OUTER_ROOT = INNER_ROOT


class Formatter(
    rich_argparse.RawTextRichHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    # argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter
    pass


(OUTER_ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
(OUTER_ROOT / "logs").mkdir(parents=True, exist_ok=True)
logger = utils.setup_logging()


PROFILE_ALIASES = {
    0: "🌀 Spin",
    12: "🐕 Walk The Dog",
    14: "🎯 Jig Step",
    15: "🐟 Bottom C6",
    16: "🐟 Bottom C12",
    17: "🐟 Bottom C17",
    18: "🐟 Bottom C30",
    19: "🐟 Bottom C35",
}


def clean_profile_name(name: str) -> str:
    banned = [
        "Beluga Venga 10000",
        "Royal Picker PM98H",
        "Fortuna Carp 360XH",
        "SAT Rigal 20 2S",
        "Reef Albacore 40 DS",
    ]

    for item in banned:
        name = name.replace(item, "")

    name = name.replace("  ", " ").strip(" |")
    return name


def setup_parser(cfg: CN) -> tuple[argparse.ArgumentParser, tuple]:
    """Configure the argument parser with all supported command-line options.

    :return: Configured ArgumentParser instance with all options and flags.
    :rtype: ArgumentParser
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("opts", nargs="*", help="overwrite configuration")

    main_parser = argparse.ArgumentParser(epilog=EPILOG, formatter_class=Formatter)
    main_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S {VERSION}"
    )

    feature_parsers = main_parser.add_subparsers(title="features", dest="feature")

    bot_parser = feature_parsers.add_parser(
        "bot",
        help="🎣 Jalankan bot mancing",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    bot_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-bot {VERSION}"
    )

    for argument in BOT_BOOLEAN_ARGUMENTS:
        flag1 = f"-{argument[0]}"
        flag2 = f"--{argument[1]}"
        help_message = argument[2]
        bot_parser.add_argument(flag1, flag2, action="store_true", help=help_message)

    profile_strategy = bot_parser.add_mutually_exclusive_group()

    def pid(_pid: str) -> int:
        return int(_pid)  # ValueError will be handled

    profile_strategy.add_argument(
        "-p",
        "--pid",
        type=pid,
        choices=range(len(cfg.PROFILE)),
        help="🎮 Pilih ID profile",
        metavar=f"{{0-{len(cfg.PROFILE) - 1}}}",
    )

    def pname(_pname: str) -> str:
        if _pname not in cfg.PROFILE:
            raise ValueError  # ValueError will be handled
        return _pname

    profile_strategy.add_argument(
        "-N",
        "--pname",
        type=pname,
        help="📝 Pilih nama profile",
        metavar="{profile name}",
    )

    def num_fish(_num_fish: str) -> int:
        return int(_num_fish)  # ValueError will be handled

    bot_parser.add_argument(
        "-n",
        "--fishes-in-keepnet",
        default=0,  # Flag is not used
        # const=0, # Flag is used but no argument given
        type=num_fish,
        choices=range(cfg.BOT.KEEPNET.CAPACITY),
        help="🐟 Tentukan jumlah ikan di keepnet (default: %(default)s)",
        metavar=f"{{0-{cfg.BOT.KEEPNET.CAPACITY - 1}}}",
    )
    bot_parser.add_argument(
        "-T",
        "--trolling",
        nargs="?",
        const="forward",
        default=None,
        type=str,
        choices=["forward", "left", "right"],
        help=(
            "🚤 Aktifkan mode trolling dan pilih arah\n"
            "(default: %(default)s, tanpa argumen: %(const)s)"
        ),
    )
    bot_parser.add_argument(
        "-R",
        "--rainbow",
        nargs="?",
        const=5,
        default=None,
        type=int,
        choices=[0, 5],
        help=(
            "🌈 Aktifkan mode rainbow dan tentukan meter angkat joran\n"
            "(default: %(default)s, tanpa argumen: %(const)s)"
        ),
    )

    bot_parser.add_argument(
        "-BT",
        "--boat-ticket",
        nargs="?",
        const=5,
        default=0,
        type=int,
        choices=[0, 1, 2, 3, 5],
        help=(
            "⛵ Aktifkan perpanjangan tiket kapal otomatis\n"
            "(default: %(default)s, tanpa argumen: %(const)s)"
        ),
    )

    craft_parser = feature_parsers.add_parser(
        "craft", help="🛠 Craft item otomatis", parents=[parent_parser], formatter_class=Formatter
    )
    craft_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-craft {VERSION}"
    )
    craft_parser.add_argument(
        "-d",
        "--discard",
        action="store_true",
        help="discard all the crafted items (for groundbaits)",
    )
    craft_parser.add_argument(
        "-i",
        "--ignore",
        action="store_true",
        help="ignore unselected material slots",
    )
    craft_parser.add_argument(
        "-n",
        "--craft-limit",
        type=int,
        default=-1,
        help="specify the number of items to craft, (default: %(default)s)",
        metavar="{number of items}",
    )

    move_parser = feature_parsers.add_parser(
        "move",
        help="🚶 Jalan otomatis",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    move_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-move {VERSION}"
    )
    move_parser.add_argument(
        "-s",
        "--shift",
        action="store_true",
        help="⌨ Tahan tombol Shift saat berjalan",
    )

    harvest_parser = feature_parsers.add_parser(
        "harvest",
        help="🪱 Cari umpan otomatis",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    harvest_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-harvest {VERSION}"
    )
    harvest_parser.add_argument(
        "-r",
        "--refill",
        action="store_true",
        help="🥕 Isi ulang hunger & comfort dengan teh dan wortel",
    )

    friction_brake_parser = feature_parsers.add_parser(
        "frictionbrake",
        help="⚙ Otomatis atur drag",
        aliases=["fb"],
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    friction_brake_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-frictionbrake {VERSION}"
    )

    calculate_paser = feature_parsers.add_parser(
        "calculate",
        help="📊 Kalkulator setup",
        aliases=["cal"],
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    calculate_paser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-calculate {VERSION}"
    )

    return main_parser, (
        bot_parser,
        craft_parser,
        move_parser,
        harvest_parser,
        friction_brake_parser,
        calculate_paser,
    )


def display_features() -> None:
    """Display a table of available features for user selection.

    Shows a formatted table with feature IDs and names.
    """
    table = Table(
        "Features",
        title="🎮 SIIYKI CONTROL PANEL 🎮",
        show_header=False,
        box=box.HEAVY,
        min_width=36,
    )

    for i, feature in enumerate(FEATURES):
        table.add_row(f"{i:>2}. {feature['name']}")
    print(table)


def get_fid(parser: argparse.ArgumentParser) -> int:
    """Prompt the user to enter a feature ID and validate the input.

    Continuously prompts until a valid feature ID is entered or the
    user chooses to quit.
    """
    utils.print_usage_box("🎣 Pilih fitur SIIYKI | h = bantuan | q = keluar")

    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and 0 <= int(user_input) < len(FEATURES):
            break
        if user_input == "q":
            print("Bye.")
            sys.exit()
        if user_input == "h":
            parser.print_help()
            continue
        utils.print_error("Invalid input, please try again.")
    return int(user_input)


def get_launch_options(parser: argparse.ArgumentParser) -> str:
    utils.print_usage_box(
        "🎮 Masukkan opsi launch | Enter = lanjut | h = bantuan | q = keluar"
    )
    while True:
        user_input = input(">>> ")
        if user_input == "q":
            print("Bye.")
            sys.exit()
        if user_input == "h":
            parser.print_help()
            continue
        break
    return user_input


def get_language():
    utils.print_usage_box("🌐 Pilih bahasa game | (1) EN | (2) RU | q = keluar")
    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and user_input in ("1", "2"):
            break
        if user_input == "q":
            print("Bye.")
            sys.exit()
        utils.print_error("Invalid input, please try again.")
    return '"en"' if user_input == "1" else '"ru"'


def get_click_lock():
    utils.print_usage_box("🖱 Apakah Windows ClickLock aktif? | (1) ya | (2) tidak | q = keluar")
    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and user_input in ("1", "2"):
            break
        if user_input == "q":
            print("Bye.")
            sys.exit()
        utils.print_error("Invalid input, please try again.")
    return "true" if user_input == "1" else "false"


def setup_cfg():
    config_path = OUTER_ROOT / "config.yaml"
    if not config_path.exists():
        language = get_language()
        click_lock = get_click_lock()

        with open(Path(INNER_ROOT / "rf4s/config/config.yaml"), "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith("LANGUAGE:"):
                    lines[i] = f"LANGUAGE: {language}\n"
                if line.startswith("  CLICK_LOCK"):
                    lines[i] = f"  CLICK_LOCK: {click_lock}\n"

        with open(config_path, "w") as file:  # shutil.copy
            file.writelines(lines)

    cfg = config.load_cfg()
    if Version(cfg.VERSION) < Version(MINIMUM_COMPATIBLE_CONFIG_VERSION):
        logger.critical(
            "Incompatible config version, some settings has been removed or deprecated\n"
            "You can delete it to allow the bot to create a new one\n"
            "Alternatively, see the CHANGELOG to modify config.yaml"
        )
        utils.safe_exit()
    return cfg


def main() -> None:
    cfg = setup_cfg()

    # CLEAN PROFILE NAMES
    banned_names = [
        "Beluga Venga 10000",
        "Royal Picker PM98H",
        "Fortuna Carp 360XH",
        "SAT Rigal 20 2S",
        "Reef Albacore 40 DS",
    ]

    for profile in cfg.PROFILE:
        if hasattr(profile, 'NAME'):
            for banned in banned_names:
                profile.NAME = profile.NAME.replace(banned, '')
            profile.NAME = profile.NAME.replace('  ', ' ').strip(' |')
    parser, subparsers = setup_parser(cfg)
    args = parser.parse_args()  # First parse to get {command} {flags}
    utils.print_logo_box(LOGO)  # Print logo here so the help message will not show it

    # If user run the program without specifying a command or by double-clicking,
    # prompt user to input the feature and launch options. This handle both Python
    # interpreter and Nuitka executable use cases.
    # If a command is parsed, we assume that the user has already typed the
    # launch options and don't prompt them to type it.
    if args.feature is None:
        display_features()
        fid = get_fid(parser)

        shortcut_features = {"jigstep", "walkdog", "spinauto", "bottomauto", "wakydrift"}

        shortcut_map = {
            "jigstep": ["bot", "-t", "-c", "-s", "-R", "5", "-p", "14"],
            "walkdog": ["bot", "-t", "-c", "-s", "-R", "5", "-p", "12"],
            "spinauto": ["bot", "-t", "-c", "-s", "-R", "5", "-p", "0"],
            "bottomauto": ["bot", "-t", "-c", "-s", "-R", "5", "-p", "15"],
            "wakydrift": ["bot", "-t", "-c", "-s", "-R", "5", "-p", "34"],
        }

        selected_command = FEATURES[fid]["command"]

        if selected_command in shortcut_map:
            sys.argv = [sys.argv[0]] + shortcut_map[selected_command]
        else:
            sys.argv = [sys.argv[0]] + [selected_command] + sys.argv[1:]
            target_parser = subparsers[fid] if fid < len(subparsers) else parser
            sys.argv += shlex.split(get_launch_options(target_parser))

        args = parser.parse_args()

    start, end = sys.argv[:2], sys.argv[2:]
    match args.feature:
        case "bot":
            sys.argv = start + shlex.split(cfg.BOT.LAUNCH_OPTIONS) + end
            App = BotApp
        case "craft":
            sys.argv = start + shlex.split(cfg.CRAFT.LAUNCH_OPTIONS) + end
            App = CraftApp
        case "move":
            sys.argv = start + shlex.split(cfg.MOVE.LAUNCH_OPTIONS) + end
            App = MoveApp
        case "harvest":
            sys.argv = start + shlex.split(cfg.HARVEST.LAUNCH_OPTIONS) + end
            App = HarvestApp
        case "frictionbrake" | "fb":
            sys.argv = start + shlex.split(cfg.FRICTION_BRAKE.LAUNCH_OPTIONS) + end
            App = FrictionBrakeApp
        case "calculate" | "cal":
            App = CalculateApp

        case "jigstep":
            sys.argv = [
                sys.argv[0],
                "bot",
                "-t",
                "-c",
                "-s",
                "-R",
                "5",
                "-p",
                "14",
            ]
            App = BotApp

        case "walkdog":
            sys.argv = [
                sys.argv[0],
                "bot",
                "-t",
                "-c",
                "-s",
                "-R",
                "5",
                "-p",
                "12",
            ]
            App = BotApp

        case "spinauto":
            sys.argv = [
                sys.argv[0],
                "bot",
                "-t",
                "-c",
                "-s",
                "-R",
                "5",
                "-p",
                "0",
            ]
            App = BotApp

        case "bottomauto":
            sys.argv = [
                sys.argv[0],
                "bot",
                "-t",
                "-c",
                "-s",
                "-R",
                "5",
                "-p",
                "15",
            ]
            App = BotApp
        case "wakydrift":
            sys.argv = [
                sys.argv[0],
                "bot",
                "-t",
                "-c",
                "-s",
                "-R",
                "5",
                "-p",
                "34",
            ]
            App = BotApp
        case _:
            raise NotImplementedError("You should not reach here.")
    App(cfg, parser.parse_args(), parser).start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)
        utils.safe_exit()  # TODO
