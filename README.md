# WordCloud Generator

日本語テキストから美しいワードクラウドを生成するアプリケーション

![](https://img.shields.io/badge/language-Japanese-brightgreen) ![](https://img.shields.io/badge/platform-Windows-blue)

## 📥 ダウンロード

[Releases](https://github.com/YOUR_USERNAME/wordcloud/releases)ページから最新版をダウンロードしてください。

## ✨ 特徴

- 📝 日本語テキストに対応（MeCab形態素解析）
- 🎨 カスタマイズ可能な色とレイアウト
- 🖼️ マスク画像で自由な形状に対応
- ⚙️ 簡単な設定ファイル（config.json）
- 🪟 フルスクリーン・フレームレス表示対応
- ⌨️ キーボードショートカット対応

## 🚀 使い方

### 1. 起動

`WordCloudGenerator.exe` をダブルクリックして起動します。

初回起動時は `content/sample_text.txt` のサンプルテキストでワードクラウドが表示されます。

### 2. テキストを変更

`content/sample_text.txt` をメモ帳などで開いて、好きなテキストに書き換えます。

### 3. 再読み込み

アプリのウィンドウで **Home キー** を押すと、テキストを再読み込みして新しいワードクラウドが表示されます。

### 4. 終了

**ESC キー** を押してアプリを終了します。

## ⌨️ キーボードショートカット

| キー     | 動作                         |
| -------- | ---------------------------- |
| **Home** | テキストファイルを再読み込み |
| **ESC**  | アプリを終了                 |

## ⚙️ 設定のカスタマイズ

`config.json` をメモ帳などで開いて編集できます。

### ウィンドウ設定

```json
"window_settings": {
  "width": 1920,          // ウィンドウの幅
  "height": 1080,         // ウィンドウの高さ
  "fullscreen": true,     // 全画面表示（true/false）
  "frameless": true       // タイトルバーを非表示（true/false）
}
```

### 色の変更

```json
"wordcloud_settings": {
  "background_color": "white",  // 背景色（white, black, #FFFFFFなど）
  "colormap": "Paired"          // 文字の色パターン
}
```

**利用可能なカラーマップ:**
`Paired`, `Pastel1`, `viridis`, `plasma`, `rainbow`, `cool`, `hot` など

### マスク画像で形を変更

猫や星など、好きな形にワードクラウドを配置できます。

1. 白黒のPNG画像を用意（白い部分にテキストが配置されます）
2. `content/` フォルダに画像を保存（例：`my_shape.png`）
3. `config.json` で指定

```json
"mask_image": "content/my_shape.png"
```

**マスクを使わない場合:**

```json
"mask_image": null
```

### 除外する単語を追加

```json
"stopwords": [
  "する", "ある", "こと", "ない", "いう", "もの",
  "自分で追加したい単語"
]
```

### 最大単語数を変更

```json
"max_words": 100  // 表示する単語の最大数
```

## 📁 ファイル構成

```
WordCloudGenerator/
├── WordCloudGenerator.exe  # 実行ファイル
├── config.json            # 設定ファイル（編集可能）
├── content/
│   ├── sample_text.txt   # テキストファイル（編集可能）
│   └── cat.png           # マスク画像（差し替え可能）
└── logs/                 # ログフォルダ（自動生成）
```

## 💡 使用例

### 例1: シンプルな四角形

```json
"mask_image": null,
"background_color": "white",
"colormap": "viridis"
```

### 例2: 猫の形

```json
"mask_image": "content/cat.png",
"background_color": "white",
"colormap": "Paired"
```

### 例3: フルスクリーン・暗い背景

```json
"window_settings": {
  "fullscreen": true,
  "frameless": true
},
"wordcloud_settings": {
  "background_color": "black",
  "colormap": "plasma"
}
```

## 🔧 トラブルシューティング

### ワードクラウドが表示されない

- `content/sample_text.txt` にテキストが入っているか確認
- テキストが短すぎる場合は、もっと長い文章を入力してください

### マスクが反映されない

- PNG画像であることを確認
- `config.json` のパスが正しいか確認
- 画像ファイル名に日本語が含まれている場合は、英数字に変更してください

### ウィンドウを閉じられない

- **ESC キー** を押してください
- または、Alt + F4 で終了できます

## 📝 開発者向け情報

### 必要な環境

- Python 3.12
- 必要なパッケージ: `requirements.txt` を参照

### インストール

```bash
pip install -r requirements.txt
```

### 実行

```bash
python main.py
```

### カスタムテキストファイルを指定

```bash
python main.py -i your_text.txt
```

### EXEのビルド

```bash
.\build.bat
```

## 🙏 使用ライブラリ

- [wordcloud](https://github.com/amueller/word_cloud) - ワードクラウド生成
- [MeCab](https://taku910.github.io/mecab/) - 日本語形態素解析
- [matplotlib](https://matplotlib.org/) - 描画
- [Pillow](https://python-pillow.org/) - 画像処理

