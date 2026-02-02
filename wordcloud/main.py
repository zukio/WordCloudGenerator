import pandas as pd
import numpy as np
import unicodedata
import MeCab
import re
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import argparse
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
from PIL import Image


def load_config():
    """設定ファイルを読み込む"""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"警告: 設定ファイルが見つかりません: {config_path}")
        return {}
    except Exception as e:
        print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")
        return {}


def setup_logging(config):
    """ログ設定を初期化する"""
    log_level = config.get('log_level', 'INFO')
    log_file_path = config.get('log_file', 'logs/wordcloud.log')
    max_bytes = config.get('max_log_size_mb', 10) * 1024 * 1024
    backup_count = config.get('backup_log_count', 5)

    # ログディレクトリの作成
    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # ハンドラーの設定
    handlers = [
        logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger('WordCloud')


# 1. MeCabの初期化
try:
    import ipadic
    mecab = MeCab.Tagger(ipadic.MECAB_ARGS)
except (ImportError, AttributeError):
    mecab = MeCab.Tagger()


def get_resource_path(relative_path):
    """exe化した際のリソースパスを取得

    --onedirモードの場合：
    - フォント等の埋め込みリソース: sys._MEIPASSから取得
    - config.json, sample_text.txt等の編集可能ファイル: 実行ファイルと同じディレクトリから取得
    """
    # 編集可能なファイルは実行ファイルと同じディレクトリから読み込む
    editable_files = ['config.json',
                      'content/sample_text.txt', 'content/cat.png']

    if any(relative_path.replace('\\', '/') == f for f in editable_files):
        # EXE実行時は実行ファイルのディレクトリ
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            # 通常のPython実行時
            base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, relative_path)

    # フォント等の埋め込みリソースはPyInstallerの一時フォルダから取得
    try:
        # PyInstallerで作成された一時フォルダ
        base_path = sys._MEIPASS
    except Exception:
        # 通常のPython実行時
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def mecab_tokenizer(text):
    # テキストの正規化
    replaced_text = unicodedata.normalize("NFKC", text)
    replaced_text = replaced_text.upper()
    # 記号の除去
    replaced_text = re.sub(r'[【】()（）『』　「」]', '', replaced_text)
    replaced_text = re.sub(r'[\[\［］\]]', ' ', replaced_text)
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)
    # 数字を0にする (元のコメント通りなら re.sub(r'\d+', '0', ...) ですが、除去なら空文字へ)
    replaced_text = re.sub(r'\d+\.*\d*', '', replaced_text)

    # 形態素解析の実行
    parsed_lines = mecab.parse(replaced_text).split("\n")[:-2]

    token_list = []
    for line in parsed_lines:
        # 表層形と品詞情報の分離
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        surface = parts[0]
        pos = parts[1].split(",")[0]

        # 名詞、動詞、形容詞に絞り込み
        target_pos = ["名詞", "動詞", "形容詞"]
        if pos in target_pos:
            # ひらがなのみの単語を除く判定
            if not re.compile("^[ぁ-ゖ]+$").match(surface):
                token_list.append(surface)

    return ' '.join(token_list)


# --- メイン処理 ---
if __name__ == "__main__":
    # 設定ファイル読み込み
    config = load_config()

    # ログ初期化
    logger = setup_logging(config)
    logger.info("=== WordCloud Application Started ===")
    logger.info(f"Config loaded: log_level={config.get('log_level', 'INFO')}")

    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='日本語テキストからワードクラウドを生成')
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='content/sample_text.txt',
        help='入力テキストファイルのパス (デフォルト: content/sample_text.txt)'
    )
    args = parser.parse_args()

    logger.info(f"Input file: {args.input}")

    # テキストファイルの読み込み (exe化対応)
    input_path = get_resource_path(
        args.input) if not os.path.isabs(args.input) else args.input

    def reload_wordcloud(window_width=None, window_height=None):
        """ワードクラウドを再読み込みして表示する"""
        logger.info("Reloading wordcloud...")

        # デフォルトファイルが存在しない場合は作成
        if args.input == 'content/sample_text.txt' and not os.path.exists(input_path):
            logger.info(f"Creating default file: {input_path}")
            print(f"デフォルトファイルが存在しないため作成します: {input_path}")
            os.makedirs(os.path.dirname(input_path), exist_ok=True)
            default_text = """Pythonは、オープンソースのプログラミング言語です。
データ分析や機械学習、自然言語処理などの分野で広く利用されています。
MeCabを使って日本語のテキストを解析し、ワードクラウドを作成するのは非常に楽しい作業です。
このファイルを編集して、自由にテキストを変更できます。
"""
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(default_text)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(
                f"Successfully loaded text file: {len(text)} characters")
        except FileNotFoundError:
            logger.error(f"File not found: {input_path}")
            print(f"エラー: ファイルが見つかりません: {input_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            print(f"エラー: ファイルの読み込みに失敗しました: {e}")
            return None

        # 形態素解析
        logger.info("Starting text tokenization with MeCab")
        processed_words = mecab_tokenizer(text)
        logger.info(
            f"Tokenization complete: {len(processed_words.split())} tokens")

        # ワードクラウド設定を取得
        wc_config = config.get('wordcloud_settings', {})

        # フォント設定
        font_path_config = wc_config.get(
            'font_path', 'content/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf')
        font_path = get_resource_path(font_path_config)
        if not os.path.exists(font_path):
            logger.warning(
                f"Font file not found: {font_path}, using system default")
            font_path = None
        else:
            logger.info(f"Using font: {font_path}")

        # ワードクラウド生成
        logger.info("Generating word cloud...")

        # ウィンドウサイズに基づいてワードクラウドのサイズを決定
        if window_width and window_height:
            wc_width = int(window_width)
            wc_height = int(window_height)
        else:
            wc_width = wc_config.get('width', 800)
            wc_height = wc_config.get('height', 800)

        logger.info(f"WordCloud size: {wc_width}x{wc_height}")

        # マスク画像の読み込み
        mask = None
        mask_image_path = wc_config.get('mask_image')
        if mask_image_path:
            full_mask_path = get_resource_path(mask_image_path)
            if os.path.exists(full_mask_path):
                try:
                    # 画像を読み込み
                    mask_img = Image.open(full_mask_path)
                    logger.info(
                        f"Loaded mask image: mode={mask_img.mode}, size={mask_img.size}")

                    # RGBAの場合はRGBに変換（白背景で合成）
                    if mask_img.mode == 'RGBA':
                        # 白背景を作成
                        background = Image.new(
                            'RGB', mask_img.size, (255, 255, 255))
                        background.paste(mask_img, mask=mask_img.split()[
                                         3])  # アルファチャンネルをマスクとして使用
                        mask_img = background
                        logger.info(
                            f"Converted RGBA to RGB with white background")

                    # グレースケールに変換（WordCloudのマスクとして最適）
                    mask_img = mask_img.convert('L')
                    logger.info(f"Converted to grayscale for mask")

                    # マスクをウィンドウサイズにリサイズ
                    if window_width and window_height:
                        mask_img = mask_img.resize(
                            (wc_width, wc_height), Image.LANCZOS)
                        logger.info(f"Mask resized to: {wc_width}x{wc_height}")

                    # numpy配列に変換
                    mask = np.array(mask_img)
                    logger.info(
                        f"Final mask - shape: {mask.shape}, dtype: {mask.dtype}")
                    logger.info(
                        f"Mask statistics - min: {mask.min()}, max: {mask.max()}, mean: {mask.mean():.2f}")

                except Exception as e:
                    logger.warning(f"Failed to load mask image: {e}")
                    mask = None
            else:
                logger.warning(f"Mask image not found: {full_mask_path}")

        # マスク使用時もwidth/heightを指定（サンプルコードと同様）
        if mask is not None:
            wordcloud = WordCloud(
                background_color=wc_config.get('background_color', 'white'),
                width=wc_width,
                height=wc_height,
                font_path=font_path,
                colormap=wc_config.get('colormap', 'Paired'),
                mask=mask,
                contour_width=0,
                contour_color='black',
                stopwords=wc_config.get(
                    'stopwords', ["する", "ある", "こと", "ない", "いう", "もの"]),
                max_words=wc_config.get('max_words', 100),
            ).generate(processed_words)
            logger.info("WordCloud generated with mask")
        else:
            logger.info(
                f"WordCloud generated without mask (rectangular) - size: {wc_width}x{wc_height}")
            wordcloud = WordCloud(
                background_color=wc_config.get('background_color', 'white'),
                width=wc_width,
                height=wc_height,
                font_path=font_path,
                colormap=wc_config.get('colormap', 'Paired'),
                stopwords=wc_config.get(
                    'stopwords', ["する", "ある", "こと", "ない", "いう", "もの"]),
                max_words=wc_config.get('max_words', 100),
            ).generate(processed_words)

        logger.info(
            f"Word cloud generation complete - actual size: {wordcloud.width}x{wordcloud.height}")
        return wordcloud

    def on_key_press(event):
        """キーボードイベントのハンドラー"""
        if event.key == 'home':
            logger.info("Home key pressed - reloading wordcloud")
            print("\nテキストファイルを再読み込み中...")
            plt.clf()
            # 現在のウィンドウサイズを取得
            fig = plt.gcf()
            bbox = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            width_px = int(bbox.width * fig.dpi)
            height_px = int(bbox.height * fig.dpi)
            wordcloud = reload_wordcloud(width_px, height_px)
            if wordcloud:
                frameless = config.get(
                    'window_settings', {}).get('frameless', False)
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis('off')
                if frameless:
                    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                plt.tight_layout(pad=0 if frameless else 1)
                plt.draw()
                print("再読み込み完了！")
        elif event.key == 'escape':
            logger.info("Escape key pressed - closing application")
            print("\nアプリケーションを終了します...")
            plt.close('all')

    # ウィンドウ設定を取得
    window_config = config.get('window_settings', {})
    window_width = window_config.get('width', 1200)
    window_height = window_config.get('height', 900)

    # 初回読み込み（ウィンドウサイズを渡す）
    wordcloud = reload_wordcloud(window_width, window_height)
    if not wordcloud:
        sys.exit(1)

    # 描画
    logger.info("Displaying word cloud")

    fig_width = window_width / 100  # インチに変換（DPI=100想定）
    fig_height = window_height / 100
    position_x = window_config.get('position_x')
    position_y = window_config.get('position_y')
    fullscreen = window_config.get('fullscreen', False)
    frameless = window_config.get('frameless', False)
    window_title = window_config.get('title', 'WordCloud Generator')

    # 図の作成
    fig = plt.figure(figsize=(fig_width, fig_height))
    fig.canvas.manager.set_window_title(window_title)

    # キーボードイベントを接続
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    logger.info("Keyboard shortcut registered: Home key for reload")

    # キーボードイベントを接続
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    logger.info("Keyboard shortcut registered: Home key for reload")

    # ウィンドウ位置の設定
    if position_x is not None and position_y is not None:
        manager = plt.get_current_fig_manager()
        try:
            # Tkinterバックエンドの場合
            manager.window.wm_geometry(f"+{position_x}+{position_y}")
            logger.info(
                f"Window position set to: ({position_x}, {position_y})")
        except AttributeError:
            try:
                # Qt5バックエンドの場合
                manager.window.move(position_x, position_y)
                logger.info(
                    f"Window position set to: ({position_x}, {position_y})")
            except:
                logger.warning(
                    "Window positioning not supported on this backend")

    # フルスクリーン設定
    if fullscreen:
        manager = plt.get_current_fig_manager()
        try:
            # Windowsの場合
            manager.window.state('zoomed')
        except:
            try:
                # その他の環境
                manager.full_screen_toggle()
            except:
                logger.warning(
                    "Fullscreen mode not supported on this platform")

    # フレームレス設定（タイトルバーとツールバーを非表示）
    if frameless:
        manager = plt.get_current_fig_manager()

        # matplotlibのツールバーを非表示
        try:
            manager.toolbar.setVisible(False)
            logger.info("Toolbar hidden")
        except:
            try:
                # Tkinterバックエンドの場合
                manager.toolbar.pack_forget()
                logger.info("Toolbar hidden (Tkinter)")
            except:
                logger.warning("Could not hide toolbar")

        # Windowsのタイトルバーを非表示
        try:
            # Tkinterバックエンドの場合
            manager.window.overrideredirect(True)
            logger.info("Title bar hidden (Tkinter)")
        except:
            try:
                # Qt5バックエンドの場合
                from matplotlib.backends.qt_compat import QtCore
                manager.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                manager.window.show()
                logger.info("Title bar hidden (Qt)")
            except:
                logger.warning("Could not hide title bar")

        # プロットの枠も非表示
        plt.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    else:
        plt.axis('off')

    plt.imshow(wordcloud, interpolation="bilinear")
    plt.tight_layout(pad=0 if frameless else 1)

    print("\n" + "="*60)
    print("WordCloud Generator - ウィンドウ表示中")
    print("="*60)
    print("【キーボードショートカット】")
    print("  Home キー : テキストファイルを再読み込み")
    print("  ESC キー  : アプリケーション終了")
    print("="*60 + "\n")
    plt.show()

    logger.info("=== WordCloud Application Finished ===")
