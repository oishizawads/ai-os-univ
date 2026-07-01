#!/usr/bin/env Rscript
# EDA: 内満データ.xlsx の探索的データ分析
# 日時: 2026-04-22

library(readxl)
library(tidyverse)
library(knitr)

# ============================================================================
# 1. データ読み込み
# ============================================================================
cat("=== 1. データ読み込み ===\n\n")

data_path <- "C:\\workspace\\ai-os\\study\\university\\PBL演習1\\内満データ.xlsx"
# シート名を確認
sheet_names <- excel_sheets(data_path)
cat("利用可能なシート:", paste(sheet_names, collapse=", "), "\n\n")

# 第７回シートを読み込み
df <- read_excel(data_path, sheet = "第７回")
cat("データ読み込み完了\n")
cat("データサイズ:", nrow(df), "行 ×", ncol(df), "列\n\n")

# ============================================================================
# 2. データ構造の確認
# ============================================================================
cat("=== 2. データ構造 ===\n\n")
cat("最初の5行：\n")
print(head(df, 5))
cat("\n列名：\n")
print(names(df))

cat("\n\nデータ型：\n")
print(str(df))

# ============================================================================
# 3. コア変数の確認（Q1, Q2, Q3）
# ============================================================================
cat("\n=== 3. コア満足度変数（Q1 現在, Q2 5年前, Q3 5年後）===\n\n")

# Q1, Q2, Q3が存在するかチェック
core_vars <- c("Q1.1", "Q2.1", "Q3.1")
if(all(core_vars %in% names(df))) {
  # 前処理: -1 → 0-10に変換
  df <- df %>%
    mutate(
      Q1 = if_else(`Q1.1` == -1, NA_real_, as.numeric(`Q1.1`) - 1),
      Q2 = if_else(`Q2.1` == -1, NA_real_, as.numeric(`Q2.1`) - 1),
      Q3 = if_else(`Q3.1` == -1, NA_real_, as.numeric(`Q3.1`) - 1)
    )
  
  cat("前処理完了（-1 → 0-10スケール）\n\n")
  
  # 記述統計
  summary_table <- data.frame(
    変数 = c("Q1現在", "Q2.5年前", "Q3.5年後"),
    Count = c(
      sum(!is.na(df$Q1)),
      sum(!is.na(df$Q2)),
      sum(!is.na(df$Q3))
    ),
    Mean = c(
      mean(df$Q1, na.rm=TRUE),
      mean(df$Q2, na.rm=TRUE),
      mean(df$Q3, na.rm=TRUE)
    ),
    SD = c(
      sd(df$Q1, na.rm=TRUE),
      sd(df$Q2, na.rm=TRUE),
      sd(df$Q3, na.rm=TRUE)
    ),
    Min = c(
      min(df$Q1, na.rm=TRUE),
      min(df$Q2, na.rm=TRUE),
      min(df$Q3, na.rm=TRUE)
    ),
    Median = c(
      median(df$Q1, na.rm=TRUE),
      median(df$Q2, na.rm=TRUE),
      median(df$Q3, na.rm=TRUE)
    ),
    Max = c(
      max(df$Q1, na.rm=TRUE),
      max(df$Q2, na.rm=TRUE),
      max(df$Q3, na.rm=TRUE)
    )
  )
  print(kable(summary_table, digits=2, format="simple"))
  
} else {
  cat("警告: Q1, Q2, Q3の列が見つかりません\n")
  cat("利用可能な列:", names(df)[grepl("^Q", names(df))][1:20], "\n")
}

# ============================================================================
# 4. Q1現在満足度の分布
# ============================================================================
cat("\n=== 4. Q1現在満足度の分布 ===\n\n")

if(!is.null(df$Q1)) {
  dist_q1 <- df %>%
    group_by(Q1スコア = round(Q1)) %>%
    summarise(人数 = n(), .groups='drop') %>%
    mutate(パーセント = 人数 / sum(人数) * 100)
  
  print(kable(dist_q1, digits=1, format="simple"))
  
  # グラフ出力
  cat("\nQ1分布のグラフ(テキスト):\n")
  for(i in 0:10) {
    count <- sum(df$Q1 == i, na.rm=TRUE)
    bar <- strrep("█", max(1, round(count/100)))
    cat(sprintf("%2d点: %s (%d人)\n", i, bar, count))
  }
}

# ============================================================================
# 5. 性別との関連（HQ1）
# ============================================================================
cat("\n=== 5. 性別（HQ1）との関連 ===\n\n")

sex_cols <- names(df)[grepl("^HQ1|^性別", names(df))]
if(length(sex_cols) > 0) {
  sex_col <- sex_cols[1]
  cat("性別カラム名:", sex_col, "\n")
  
  sex_dist <- df %>%
    group_by(!!sym(sex_col)) %>%
    summarise(人数 = n(), .groups='drop') %>%
    mutate(パーセント = 人数 / sum(人数) * 100)
  
  print(kable(sex_dist, digits=1, format="simple"))
  
  # Q1と性別のクロス集計
  if(!is.null(df$Q1)) {
    cat("\n性別別Q1満足度（平均±SD）:\n")
    sex_q1 <- df %>%
      group_by(!!sym(sex_col)) %>%
      summarise(
        N = sum(!is.na(Q1)),
        Mean = mean(Q1, na.rm=TRUE),
        SD = sd(Q1, na.rm=TRUE),
        Median = median(Q1, na.rm=TRUE),
        .groups='drop'
      )
    print(kable(sex_q1, digits=2, format="simple"))
  }
} else {
  cat("性別カラムが見つかりません\n")
}

# ============================================================================
# 6. 欠損値分析
# ============================================================================
cat("\n=== 6. 欠損値分析 ===\n\n")

missing_summary <- data.frame(
  列名 = names(df),
  欠損数 = colSums(is.na(df)),
  欠損率 = colSums(is.na(df)) / nrow(df) * 100
) %>%
  filter(欠損数 > 0) %>%
  arrange(desc(欠損率)) %>%
  head(20)

if(nrow(missing_summary) > 0) {
  cat("欠損値が多い列（上位20）:\n")
  print(kable(missing_summary, digits=1, format="simple"))
} else {
  cat("欠損値なし（素晴らしい!）\n")
}

# ============================================================================
# 7. 相関分析（コア変数）
# ============================================================================
cat("\n=== 7. 相関分析 ===\n\n")

numeric_cols <- df %>%
  select(where(is.numeric)) %>%
  select(starts_with("Q")) %>%
  names()

if(length(numeric_cols) > 0 && !is.null(df$Q1)) {
  cat("Q1との相関（強い順）:\n")
  
  corr_q1 <- sapply(numeric_cols, function(col) {
    cor(df[[col]], df$Q1, use="complete.obs")
  }) %>%
    sort(decreasing=TRUE) %>%
    head(15)
  
  for(i in seq_along(corr_q1)) {
    cat(sprintf("%2d. %s: r = %.3f\n", i, names(corr_q1)[i], corr_q1[i]))
  }
}

# ============================================================================
# 8. 基本統計量（全数値列）
# ============================================================================
cat("\n=== 8. 数値列の基本統計量（先頭20列）===\n\n")

numeric_summary <- df %>%
  select(where(is.numeric)) %>%
  select(1:min(20, ncol(select(df, where(is.numeric))))) %>%
  summarise(across(everything(), list(
    Mean = ~mean(., na.rm=TRUE),
    SD = ~sd(., na.rm=TRUE),
    Min = ~min(., na.rm=TRUE),
    Median = ~median(., na.rm=TRUE),
    Max = ~max(., na.rm=TRUE)
  )))

cat("先頭5列の詳細統計:\n")
print(kable(
  data.frame(
    列 = rep(names(df %>% select(where(is.numeric)) %>% select(1:5))),
    統計量 = rep(c("Mean", "SD", "Min", "Median", "Max"), 5),
    値 = as.vector(t(numeric_summary[, 1:25]))
  ) %>% head(15),
  format="simple"
))

cat("\n\n=== EDA 完了 ===\n")
