import subprocess
import sys
import platform


def setup():
    print("--- 1. Pythonパッケージのインストールを開始します ---")
    # requirements.txt を使って一括インストール
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])

    # OSがLinux（Google ColabやUbuntuなど）の場合だけフォントをインストール
    if platform.system() == "Linux":
        print("\n--- 2. Linuxシステムフォントのインストールを開始します ---")
        try:
            subprocess.check_call(["sudo", "apt-get", "update", "-q"])
            subprocess.check_call(
                ["sudo", "apt-get", "install", "-yq", "fonts-ipafont-gothic"])
        except Exception as e:
            print(f"フォントのインストールでエラーが発生しました: {e}")
    else:
        print("\n--- 2. スキップ: Windows/Macではシステムフォントの自動インストールは不要です ---")

    print("\n✨ すべての準備が整いました！")


if __name__ == "__main__":
    setup()
