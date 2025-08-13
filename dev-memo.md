#開発メモ

※このファイルはgithubに登録しないでください。

## 検出機能
insect_detector.py: 15個の独立した検出関数（YOLOv8推論、画像処理）

 - ファイル名: docs/design/detailed_design/processing/phase3/insect_detector_processing_spec.md
 - 所属フェーズ: Phase 3（検出機能）
 - 15個の関数仕様を詳細記述
 
 ## 行動分析
 insect_detector_processing_spec.md

  - ファイル名:
  docs/design/detailed_design/processing/phase4/activity_calculator_processing_spec.md
  - 所属フェーズ: Phase 4（活動量解析）
  - 時系列分析・移動距離算出・統計計算の仕様を詳細記述

## 使用パターン

  単独使用:
  ### 昆虫検出のみ
  python insect_detector.py

  ### 活動量解析のみ
  python activity_calculator.py

  統合使用:
  ### システム全体動作
  python main.py --mode single
  python main.py --mode continuous

  両機能は完全に独立したライブラリとして設計されており、単独でもmain.pyからの統合制御でも使用可能
  な柔軟な構造になっています。

    1. main.pyを使用（推奨）
  # 連続検出モード（継続観察）
  python main.py --mode continuous

  # 単発検出モード  
  python main.py --mode single

  2. 時間設定
  - 設定ファイル: config/system_config.json
  - 継続時間の設定項目:
    - detection_interval: 検出間隔（秒）
    - max_runtime_hours: 最大実行時間
    - daily_start_time: 開始時刻
    - daily_end_time: 終了時刻