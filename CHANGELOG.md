# Changelog

## Unreleased

- `client()` now works with no arguments: the scorecard's public Supabase URL
  and publishable (anon) key are built in, so you no longer set `SUPABASE_URL`
  or `SUPABASE_ANON_KEY`. The quick start is `cli = si.client()` then
  `si.sign_in(cli, email, password)`. For testing or self-hosting, override the
  defaults with the `SI_SUPABASE_URL` and `SI_SUPABASE_ANON_KEY` environment
  variables or with the arguments. Existing positional calls keep working.

## 0.2.0

- All HTTP now goes through one internal function, `socialinfrascorepy._http.perform()`.
  Errors carry the server's message and a `status_code`.
- The package runs in the browser under Pyodide: on import it calls
  `pyodide_http.patch_all()` when `pyodide-http` is installed
  (`micropip.install("pyodide-http")`). `pyodide-http` is not a dependency.
- `get_themes()` and `get_theme_keywords()` are internal now (`_get_themes()`,
  `_get_theme_keywords()`), removed from `__all__` and from the reference docs.
  The old names remain for one release as aliases that emit `DeprecationWarning`.
- `submit_request()` no longer documents `sites_grid_sqkm` or `n_keywords`.
  Both are still accepted via `**kwargs` and ignored with a warning. Because
  `n_keywords` used to be the third positional parameter, pass `name` and the
  rest by keyword.
- Sites are described as coming from Overture Maps open data throughout the docs.

## 0.1.0

- Initial release: sign-up/sign-in, polygon lookup, request submission with theme
  and grid configuration, scorecard and site downloads, account management.
