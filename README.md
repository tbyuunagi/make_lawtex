# make_lawtex
概要
日本の法令api(https://www.e-gov.go.jp/elaws/interface_api/index.html)を用いて.tex形式のファイルを生成します。
手持ちの六法に載っていない法律を勉強する際などにご利用ください。
# 使い方
pythonでmake_lawtex.pyを実行して言われたとおりにすればlawsのディレクトリ内に"法令名".xml（法令apiから取得したもの）と"法令名".texのファイルが生成されます。
"法令名".texのファイルをコンパイル(lualatexによるコンパイルを想定)すればサンプルのようなPdfが出来上がります。
