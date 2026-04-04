# create-claude-md

## Objective
新しいプロジェクトに対して、そのプロジェクト専用の `CLAUDE.md` 初稿を作成する。

## Supported Project Types
- competition
- client-project
- company-space
- internal-tooling

## Required Inputs
以下を整理してから書く。
- project type
- project goal
- must-read files
- key constraints
- directory rules
- review focus
- workflow rules

## Writing Rules
- そのプロジェクトで本当に使うルールだけを書く
- グローバルルールのコピペだけで埋めない
- 競技なら再現性、業務なら要件整合性を軸にする
- `src/` と `ai-src/` の役割分離は原則として明記する
- 読む順番を必ず入れる
- 何を重度リスク扱いするかも入れる

## Structure
以下の構成で出力する。

# <Project Name> - CLAUDE.md

## Goal

## Read First

## Principles

## Directory Rules

## Workflow

## Review Focus

## Warnings

## Output Format
出力は**そのまま保存できる完成版Markdown全文**にする。
前置きや説明は不要。