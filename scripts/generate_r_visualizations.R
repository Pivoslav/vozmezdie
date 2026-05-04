#!/usr/bin/env Rscript
# Generate R visualizations from comparison_results.json
# Requires: R with packages jsonlite, ggplot2, ggdendro
# Install: install.packages(c("jsonlite", "ggplot2", "ggdendro"))
#
# Usage: Rscript scripts/generate_r_visualizations.R [path/to/comparison_results.json] [output_dir]

args <- commandArgs(trailingOnly = TRUE)
json_path <- if (length(args) >= 1) args[1] else "data/output/comparison_results.json"
out_dir <- if (length(args) >= 2) args[2] else "data/output/r_plots"

# Resolve paths: if relative, assume run from project root
if (!grepl("^[/\\\\]|[A-Za-z]:", json_path)) json_path <- file.path(getwd(), json_path)
if (!grepl("^[/\\\\]|[A-Za-z]:", out_dir)) out_dir <- file.path(getwd(), out_dir)

if (!file.exists(json_path)) {
  message("Comparison results not found: ", json_path)
  quit(save = "no", status = 1)
}

dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

# Load data
data <- jsonlite::read_json(json_path, simplifyVector = TRUE)
comp <- data$comparison_by_doc
if (is.null(comp) || length(comp) == 0) {
  message("No comparison_by_doc in JSON")
  quit(save = "no", status = 1)
}

# Collect aligned rows (handle list-of-lists from JSON)
collect_rows <- function(ar, doc_id) {
  if (is.null(ar) || length(ar) == 0) return(NULL)
  if (is.data.frame(ar)) {
    ar$doc_id <- doc_id
    return(ar)
  }
  df <- do.call(rbind, lapply(ar, function(r) as.data.frame(r, stringsAsFactors = FALSE)))
  if (is.null(df) || nrow(df) == 0) return(NULL)
  df$doc_id <- doc_id
  df
}
rows <- do.call(rbind, lapply(names(comp), function(doc_id) collect_rows(comp[[doc_id]]$aligned_rows, doc_id)))
if (is.null(rows) || nrow(rows) == 0) {
  message("No aligned rows")
  quit(save = "no", status = 1)
}

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  message("Install ggplot2: install.packages('ggplot2')")
  quit(save = "no", status = 1)
}
library(ggplot2)

# Normalize labels (Generic / Neutral variants)
norm <- function(x) {
  x <- trimws(as.character(x))
  x[x == ""] <- NA
  x[tolower(x) %in% c("generic / neutral", "generic / neutral language")] <- "Generic / Neutral Language"
  x
}
rows$llm_framing <- norm(rows$llm_framing)
rows$human_framing <- norm(rows$human_framing)
rows$llm_category <- norm(rows$llm_category)
rows$human_category <- norm(rows$human_category)

# Drop rows with missing labels
rows <- rows[!is.na(rows$llm_framing) & !is.na(rows$human_framing), , drop = FALSE]
if (nrow(rows) == 0) {
  message("No rows with both LLM and human framing")
  quit(save = "no", status = 1)
}

# Aggregate framing flow
fram_tbl <- as.data.frame(table(
  llm_framing = rows$llm_framing,
  human_framing = rows$human_framing
))
names(fram_tbl)[3] <- "n"
fram_flow <- fram_tbl[fram_tbl$n > 0, , drop = FALSE]

# Aggregate category flow (if both present)
rows_cat <- rows[!is.na(rows$llm_category) & !is.na(rows$human_category), , drop = FALSE]
cat_flow <- NULL
if (nrow(rows_cat) > 0) {
  cat_tbl <- as.data.frame(table(
    llm_category = rows_cat$llm_category,
    human_category = rows_cat$human_category
  ))
  names(cat_tbl)[3] <- "n"
  cat_flow <- cat_tbl[cat_tbl$n > 0, , drop = FALSE]
}

# Project palette (archival browns)
palette <- c(
  "#8b0000", "#2d5a27", "#4a5568", "#8b7355", "#2563eb",
  "#ca8a04", "#0d9488", "#7c3aed", "#dc2626", "#15803d"
)

# Truncate long labels to avoid overflow (max chars, add ellipsis)
trunc_label <- function(x, max_len = 22) {
  x <- as.character(x)
  ifelse(nchar(x) > max_len, paste0(substr(x, 1, max_len - 3), "..."), x)
}

# Heatmap: LLM Framing x Human Framing (replaces alluvial - no overflow)
if (nrow(fram_flow) > 0) {
  p_fram <- ggplot2::ggplot(fram_flow, ggplot2::aes(x = human_framing, y = llm_framing, fill = n)) +
    ggplot2::geom_tile(colour = "white", linewidth = 0.5) +
    ggplot2::geom_text(ggplot2::aes(label = n), size = 3, colour = "black") +
    ggplot2::scale_fill_gradient(low = "#f5f0e8", high = "#8b7355", na.value = "white") +
    ggplot2::labs(
      title = "LLM vs Human Framing",
      subtitle = "Cell = count of segments. Diagonal = agreement.",
      x = "Human label",
      y = "LLM label",
      fill = "Count"
    ) +
    ggplot2::theme_minimal() +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(angle = 45, hjust = 1, size = 8),
      axis.text.y = ggplot2::element_text(size = 8),
      legend.position = "right",
      plot.margin = ggplot2::margin(10, 10, 10, 10),
      panel.grid = ggplot2::element_blank()
    )
  n_fram <- length(unique(c(fram_flow$llm_framing, fram_flow$human_framing)))
  w_fram <- 8 + n_fram * 0.8
  h_fram <- 6 + n_fram * 0.5
  out_fram <- file.path(out_dir, "alluvial_framing.png")
  ggplot2::ggsave(out_fram, p_fram, width = min(w_fram, 16), height = min(h_fram, 12), dpi = 120, bg = "white")
  message("Wrote ", out_fram)
}

# Heatmap: LLM Category x Human Category (replaces alluvial - no overflow)
if (!is.null(cat_flow) && nrow(cat_flow) > 0) {
  p_cat <- ggplot2::ggplot(cat_flow, ggplot2::aes(x = human_category, y = llm_category, fill = n)) +
    ggplot2::geom_tile(colour = "white", linewidth = 0.5) +
    ggplot2::geom_text(ggplot2::aes(label = n), size = 2.5, colour = "black") +
    ggplot2::scale_fill_gradient(low = "#f5f0e8", high = "#8b7355", na.value = "white") +
    ggplot2::labs(
      title = "LLM vs Human Category",
      subtitle = "Cell = count of segments. Diagonal = agreement.",
      x = "Human label",
      y = "LLM label",
      fill = "Count"
    ) +
    ggplot2::theme_minimal() +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(angle = 45, hjust = 1, size = 7),
      axis.text.y = ggplot2::element_text(size = 7),
      legend.position = "right",
      plot.margin = ggplot2::margin(10, 10, 10, 10),
      panel.grid = ggplot2::element_blank()
    )
  n_cat <- length(unique(c(cat_flow$llm_category, cat_flow$human_category)))
  w_cat <- 10 + n_cat * 0.6
  h_cat <- 7 + n_cat * 0.4
  out_cat <- file.path(out_dir, "alluvial_category.png")
  ggplot2::ggsave(out_cat, p_cat, width = min(w_cat, 20), height = min(h_cat, 14), dpi = 120, bg = "white")
  message("Wrote ", out_cat)
}

# --- Dendrogram: use ggdendrogram() wrapper with leaf_labels=TRUE ---
if (requireNamespace("ggdendro", quietly = TRUE)) {
  library(ggdendro)
  fram_levels <- unique(c(rows$llm_framing, rows$human_framing))
  fram_levels <- fram_levels[!is.na(fram_levels) & fram_levels != ""]
  if (length(fram_levels) > 0) {
    doc_fram_tbl <- as.data.frame(table(
      doc_id = rows$doc_id,
      llm_framing = rows$llm_framing
    ))
    doc_fram_tbl <- doc_fram_tbl[doc_fram_tbl$Freq > 0, , drop = FALSE]
    doc_mat <- xtabs(Freq ~ doc_id + llm_framing, data = doc_fram_tbl)
    doc_mat <- as.matrix(doc_mat)
    total <- rowSums(doc_mat)
    doc_mat <- doc_mat / (total %*% matrix(1, 1, ncol(doc_mat)))
    doc_mat[is.nan(doc_mat)] <- 0
    if (nrow(doc_mat) >= 2) {
      d <- dist(doc_mat, method = "euclidean")
      hc <- hclust(d, method = "ward.D2")
      docs <- data$documents
      if (!is.null(docs) && length(docs) > 0) {
        nvl <- function(x, y) if (is.null(x) || (length(x) == 1 && identical(x, ""))) y else x
        if (is.data.frame(docs)) {
          disp <- docs$display_name
          ids <- docs$document_id
        } else {
          disp <- sapply(docs, function(x) nvl(x$display_name, nvl(x$document_id, "")))
          ids <- sapply(docs, function(x) nvl(x$document_id, ""))
        }
        lbl_map <- setNames(disp, ids)
        hc$labels <- ifelse(hc$labels %in% names(lbl_map), lbl_map[hc$labels], hc$labels)
      }
      hc$labels <- trunc_label(hc$labels, max_len = 20)
      dg <- as.dendrogram(hc)
      n_docs <- nrow(doc_mat)
      h_dendro <- max(6, 4 + n_docs * 0.5)
      w_dendro <- 12
      p_dendro <- ggdendro::ggdendrogram(dg, rotate = TRUE, size = 2, leaf_labels = TRUE) +
        ggplot2::labs(
          title = "Document Clustering by Framing Profile",
          subtitle = "Documents with similar framing mix cluster together. Ward.D2 method."
        ) +
        ggplot2::theme(
          plot.title = ggplot2::element_text(hjust = 0.5),
          plot.subtitle = ggplot2::element_text(hjust = 0.5, size = 9),
          plot.margin = ggplot2::margin(10, 10, 10, 10),
          axis.text.y = ggplot2::element_text(size = 9)
        )
      out_dendro <- file.path(out_dir, "dendrogram_documents.png")
      ggplot2::ggsave(out_dendro, p_dendro, width = w_dendro, height = h_dendro, dpi = 120, bg = "white")
      message("Wrote ", out_dendro)
    }
  }
}

# --- Segment length vs accuracy: binned bar chart (proportion correct by length bucket) ---
rows_all <- do.call(rbind, lapply(names(comp), function(doc_id) collect_rows(comp[[doc_id]]$aligned_rows, doc_id)))
if (!is.null(rows_all) && nrow(rows_all) > 0) {
  rows_all$length <- pmax(
    nchar(as.character(ifelse(is.null(rows_all$entry_eng), "", rows_all$entry_eng))),
    nchar(as.character(ifelse(is.null(rows_all$entry_rus), "", rows_all$entry_rus)))
  )
  rows_all$match <- as.integer(ifelse(is.null(rows_all$both_match) | is.na(rows_all$both_match), FALSE, rows_all$both_match))
  seg_df <- data.frame(
    length = rows_all$length,
    match = rows_all$match
  )
  seg_df <- seg_df[seg_df$length > 0 & seg_df$length < 5000, , drop = FALSE]
  if (nrow(seg_df) > 50) {
    breaks <- c(0, 50, 100, 150, 200, 300, 500, 1000, 10000)
    seg_df$bucket <- cut(seg_df$length, breaks = breaks, labels = c("0-50", "51-100", "101-150", "151-200", "201-300", "301-500", "501-1000", "1000+"), include.lowest = TRUE)
    seg_df <- seg_df[!is.na(seg_df$bucket), , drop = FALSE]
    if (nrow(seg_df) > 0) {
      bin_df <- stats::aggregate(match ~ bucket, data = seg_df, FUN = length)
      names(bin_df)[2] <- "n"
      bin_df$pct <- 100 * stats::aggregate(match ~ bucket, data = seg_df, FUN = mean)$match
    } else {
      bin_df <- data.frame()
    }
    if (nrow(bin_df) >= 1) {
      p_seg <- ggplot2::ggplot(bin_df, ggplot2::aes(x = bucket, y = pct)) +
        ggplot2::geom_col(fill = "#8b7355", width = 0.7) +
        ggplot2::geom_text(ggplot2::aes(label = sprintf("%.0f%%", pct)), vjust = -0.3, size = 3) +
        ggplot2::labs(
          title = "Accuracy by segment length",
          subtitle = "Bars = % of segments where LLM matched both category and framing (vs human). Longer segments may have more context.",
          x = "Segment length (characters)",
          y = "% correct (both match)"
        ) +
        ggplot2::theme_minimal() +
        ggplot2::theme(
          plot.margin = ggplot2::margin(10, 10, 10, 10),
          axis.text.x = ggplot2::element_text(angle = 45, hjust = 1)
        ) +
        ggplot2::ylim(0, max(c(bin_df$pct, 50), na.rm = TRUE) * 1.15)
      out_seg <- file.path(out_dir, "segment_length_accuracy.png")
      ggplot2::ggsave(out_seg, p_seg, width = 9, height = 5, dpi = 120, bg = "white")
      message("Wrote ", out_seg)
    }
  }
}

message("Done.")
