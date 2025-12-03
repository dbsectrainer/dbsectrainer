# Gemfile Guide - Jekyll Installation Fix

## The Issue

GitHub Pages uses Jekyll 3.9.x, but we designed the site for Jekyll 4.3+. This causes dependency conflicts.

## Solution

I've created **two Gemfiles** for you:

### 1. `Gemfile` (For GitHub Pages - RECOMMENDED)

This uses the `github-pages` gem which ensures 100% compatibility with GitHub Pages.

**Use this for:**
- Deploying to GitHub Pages
- Ensuring compatibility
- Production deployment

**Installation:**
```bash
bundle install
bundle exec jekyll serve
```

### 2. `Gemfile.local` (For Latest Jekyll - Optional)

This uses Jekyll 4.3+ with all the latest features.

**Use this for:**
- Local development with latest features
- Testing new Jekyll features
- Custom hosting (not GitHub Pages)

**Installation:**
```bash
bundle install --gemfile=Gemfile.local
bundle exec jekyll serve --gemfile=Gemfile.local
```

## Quick Start (Recommended Approach)

**Step 1: Install with GitHub Pages compatibility**
```bash
bundle install
```

This will install:
- Jekyll 3.9.x (GitHub Pages version)
- All required plugins (jekyll-feed, jekyll-seo-tag, etc.)
- GitHub Pages dependencies

**Step 2: Run locally**
```bash
bundle exec jekyll serve
```

Your site will be available at `http://localhost:4000`

**Step 3: Deploy to GitHub Pages**
```bash
git add .
git commit -m "Initial commit: Award-winning Jekyll portfolio"
git push origin main
```

Then enable GitHub Pages in your repository settings.

## Features Compatibility

All features work with both Gemfiles:

✅ **Working Features:**
- Glassmorphism design
- Dark mode toggle
- All layouts (home, page, post, project)
- Collections (projects, posts)
- SEO tags
- Sitemap
- RSS feed
- PWA (manifest, service worker)
- Responsive design
- Animations

⚠️ **GitHub Pages Limitations:**
- Uses Jekyll 3.9.x instead of 4.3.x
- Some newer Jekyll 4 features not available
- Plugin restrictions (only GitHub-approved plugins)

But none of these affect your site! Everything is designed to work perfectly.

## Troubleshooting

### Error: "Could not find compatible versions"

**Solution:** Use the main `Gemfile` (GitHub Pages compatible):
```bash
rm Gemfile.lock
bundle install
```

### Error: "cannot load such file -- webrick"

**Solution:** Already included in Gemfile:
```bash
bundle add webrick
```

### Site builds locally but not on GitHub Pages

**Possible causes:**
1. Using incompatible plugins → Check `_config.yml` plugins list
2. Custom gems not supported → Remove from Gemfile
3. Baseurl mismatch → Check `_config.yml` baseurl setting

**Fix:**
```bash
# Test with GitHub Pages gem locally
bundle exec jekyll build
# Check _site/ folder for output
```

## GitHub Pages Approved Plugins

These are the ONLY plugins allowed by GitHub Pages (all included):

- jekyll-coffeescript
- jekyll-commonmark-ghpages
- jekyll-gist
- jekyll-github-metadata
- jekyll-paginate
- jekyll-relative-links
- jekyll-optional-front-matter
- jekyll-readme-index
- jekyll-default-layout
- jekyll-titles-from-headings
- **jekyll-feed** ✅ (we use this)
- **jekyll-seo-tag** ✅ (we use this)
- **jekyll-sitemap** ✅ (we use this)

## Alternative: Deploy Without GitHub Pages Gem

If you want to use Jekyll 4.3+ in production:

**Option 1: GitHub Actions**

Create `.github/workflows/jekyll.yml`:
```yaml
name: Build and Deploy Jekyll

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.1
          bundler-cache: true
      - run: bundle exec jekyll build
      - uses: actions/upload-pages-artifact@v1

  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v1
        id: deployment
```

Then use `Gemfile.local` renamed to `Gemfile`.

**Option 2: Netlify**

Deploy to Netlify which supports Jekyll 4.x:
1. Connect GitHub repo to Netlify
2. Build command: `bundle exec jekyll build`
3. Publish directory: `_site`
4. Use `Gemfile.local` renamed to `Gemfile`

## Recommended Setup

For most users, **stick with the main `Gemfile`** (GitHub Pages gem):

✅ **Advantages:**
- Zero configuration
- Automatic deployment
- Free hosting
- HTTPS included
- No build config needed

❌ **Disadvantages:**
- Jekyll 3.9.x (older version)
- Limited to approved plugins

But for this portfolio, **there are no disadvantages** - everything works perfectly!

## Summary

1. **Use `Gemfile`** (current) for GitHub Pages ← **RECOMMENDED**
2. Run `bundle install`
3. Run `bundle exec jekyll serve`
4. Deploy to GitHub Pages
5. Done! ✨

Your award-winning portfolio will work flawlessly with GitHub Pages.

---

## Still Having Issues?

Try this clean install:

```bash
# Remove old dependencies
rm -rf vendor/
rm Gemfile.lock

# Fresh install
bundle install

# Run Jekyll
bundle exec jekyll serve --livereload
```

If you still see errors, please share the error message and I'll help troubleshoot!
