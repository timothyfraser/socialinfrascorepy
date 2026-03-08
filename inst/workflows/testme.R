#!/usr/bin/env Rscript

# Local preview helper for the socialinfrascorepy quartodoc website.
# Builds from socialinfrascorepy/docs and serves docs/socialinfrascorepy
# so local preview matches the Netlify publish directory.

if (nzchar(Sys.which("quarto")) == FALSE) {
  stop(
    "Quarto CLI not found on PATH. Install from https://quarto.org/docs/get-started/",
    call. = FALSE
  )
}

if (nzchar(Sys.which("quartodoc")) == FALSE) {
  stop(
    "quartodoc CLI not found on PATH. Install with: pip install quartodoc",
    call. = FALSE
  )
}

if (nzchar(Sys.which("python")) == FALSE) {
  stop(
    "Python not found on PATH. Needed to serve docs/socialinfrascorepy locally.",
    call. = FALSE
  )
}

repo_root = getwd()
if (basename(repo_root) == "socialinfrascorepy") {
  repo_root = normalizePath(file.path(repo_root, ".."), mustWork = TRUE)
}

source_docs_dir = file.path(repo_root, "socialinfrascorepy", "docs")
site_build_dir = file.path(source_docs_dir, "_site")
publish_dir = file.path(repo_root, "docs", "socialinfrascorepy")

if (!dir.exists(source_docs_dir)) {
  stop("Could not find source docs directory: ", source_docs_dir, call. = FALSE)
}

old_wd = getwd()
setwd(repo_root)
on.exit(setwd(old_wd), add = TRUE)

message("Building quartodoc reference pages...")
status_build = system2(
  "quartodoc",
  c("build", "--config", "socialinfrascorepy/docs/_quarto.yml"),
  stdout = "",
  stderr = ""
)
if (status_build != 0) {
  stop("quartodoc build failed.", call. = FALSE)
}

message("Rendering docs site...")
status_render = system2(
  "quarto",
  c("render", "socialinfrascorepy/docs"),
  stdout = "",
  stderr = ""
)
if (status_render != 0) {
  stop("quarto render failed.", call. = FALSE)
}

if (!dir.exists(site_build_dir)) {
  stop("Rendered site folder not found: ", site_build_dir, call. = FALSE)
}

if (dir.exists(publish_dir)) {
  unlink(publish_dir, recursive = TRUE, force = TRUE)
}
dir.create(publish_dir, recursive = TRUE, showWarnings = FALSE)
file.copy(
  from = list.files(site_build_dir, full.names = TRUE, all.files = TRUE, no.. = TRUE),
  to = publish_dir,
  recursive = TRUE
)
unlink(site_build_dir, recursive = TRUE, force = TRUE)
unlink(file.path(source_docs_dir, ".quarto"), recursive = TRUE, force = TRUE)
unlink(file.path(source_docs_dir, "reference"), recursive = TRUE, force = TRUE)
unlink(file.path(source_docs_dir, "objects.json"), recursive = FALSE, force = TRUE)

if (!file.exists(file.path(publish_dir, "index.html"))) {
  stop("Rendered homepage not found: ", file.path(publish_dir, "index.html"), call. = FALSE)
}

message("Local published copy ready at: ", publish_dir)
message("Starting local server at http://127.0.0.1:4848 (Ctrl+C to stop)...")
system2(
  "python",
  c("-m", "http.server", "4848", "--bind", "127.0.0.1", "--directory", publish_dir),
  stdout = "",
  stderr = ""
)

browseURL("https://localhost:4848")