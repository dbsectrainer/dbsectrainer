# Deployment Guide - Award-Winning Jekyll Portfolio

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Updated personal information in `_config.yml`
- [ ] Added professional profile photo to `assets/images/profile/profile.jpg`
- [ ] Added project screenshots to `assets/images/projects/`
- [ ] Created app icons for PWA (72x72 to 512x512)
- [ ] Updated social links in `_data/social.yml`
- [ ] Added blog post images to `assets/images/blog/`
- [ ] Created resume PDF at `assets/files/resume.pdf`
- [ ] Tested locally with `bundle exec jekyll serve`

## 🚀 GitHub Pages Deployment

### Step 1: Prepare Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Award-winning Jekyll portfolio site

- Modern glassmorphism design with dark mode
- PWA with offline support
- 5 comprehensive project showcases
- AI/ML security blog posts
- Responsive mobile-first design
- SEO optimized with Jekyll SEO tag
- Performance optimized (Lighthouse 90+ target)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/dbsectrainer/dbsectrainer.github.io.git

# Push to GitHub
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/` (root)
4. Click **Save**
5. Wait 2-5 minutes for deployment

Your site will be live at: `https://dbsectrainer.github.io`

### Step 3: Custom Domain (Optional)

If you have a custom domain:

1. Create `CNAME` file:
```bash
echo "yourdomain.com" > CNAME
git add CNAME
git commit -m "Add custom domain"
git push
```

2. Configure DNS:
```
Type: A
Name: @
Value: 185.199.108.153
       185.199.109.153
       185.199.110.153
       185.199.111.153

Type: CNAME
Name: www
Value: dbsectrainer.github.io
```

3. Enable HTTPS in GitHub Pages settings

## 🎨 Customization Steps

### 1. Update Site Information

Edit `_config.yml`:

```yaml
title: Your Name | Your Title
email: your.email@example.com
description: >-
  Your professional bio

author:
  name: Your Name
  title: Your Professional Title
  bio: >-
    Your detailed bio
  location: Your Location
  linkedin: your-linkedin-username
  github: your-github-username
  email: your.email@example.com
```

### 2. Add Profile Photo

1. Take/obtain professional headshot
2. Resize to 300x300px (square)
3. Save as `assets/images/profile/profile.jpg`
4. Optimize with tools like TinyPNG

### 3. Add Project Images

For each project:

```bash
# Create project images (recommended: 1200x630px)
assets/images/projects/
  ├── global-ai-dashboard.png
  ├── mandarin-pathways.png
  ├── enterprise-checklists.png
  ├── cloud-security.png
  └── security-scanner.png
```

### 4. Create PWA Icons

Generate icons using tools like [PWA Asset Generator](https://www.pwabuilder.com/):

Required sizes:
- 72x72, 96x96, 128x128, 144x144
- 152x152, 192x192, 384x384, 512x512

Save to `assets/images/icons/`

### 5. Update Resume

1. Create professional resume PDF
2. Save as `assets/files/resume.pdf`
3. Ensure it's under 2MB for fast downloads

### 6. Customize Colors (Optional)

Edit `_sass/_variables.scss`:

```scss
:root {
  // Your brand colors
  --primary-600: #your-primary-color;
  --secondary-600: #your-secondary-color;
  --accent-600: #your-accent-color;
}
```

## 🧪 Testing

### Local Testing

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve --livereload

# Test on different devices
# Visit http://localhost:4000 on your phone/tablet
```

### Performance Testing

1. **Lighthouse Audit** (Chrome DevTools)
   - Open site in Chrome
   - F12 → Lighthouse tab
   - Run audit
   - Target: 90+ in all categories

2. **Mobile Responsiveness**
   - Chrome DevTools → Toggle device toolbar
   - Test various screen sizes
   - Check touch targets (44x44px minimum)

3. **PWA Testing**
   - Chrome DevTools → Application tab
   - Check Service Worker registration
   - Test offline mode (Network → Offline)
   - Verify manifest.json

### Browser Compatibility

Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📊 Analytics Setup

### Google Analytics

1. Create Google Analytics account
2. Get tracking ID
3. Update `_config.yml`:
```yaml
google_analytics: UA-XXXXXXXXX-X
```

### Alternative: Plausible Analytics

```html
<!-- Add to _includes/head.html -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## 🔒 Security

### Best Practices

1. **Keep Dependencies Updated**
```bash
bundle update
```

2. **Security Headers** (via GitHub Pages settings)
   - Already configured in `_config.yml`
   - X-Frame-Options, X-Content-Type-Options, etc.

3. **Content Security Policy**
   - Consider adding via meta tag if needed
   - Test with browser console

## 🐛 Troubleshooting

### Build Fails

```bash
# Clear Jekyll cache
bundle exec jekyll clean

# Update gems
bundle update

# Check for errors
bundle exec jekyll build --verbose
```

### GitHub Pages 404

- Ensure `index.html` exists in root
- Check `_config.yml` for errors
- Verify branch/folder settings in GitHub Pages

### Service Worker Not Loading

- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+F5` (Windows)
- Check browser console for errors
- Ensure HTTPS is enabled

### Images Not Showing

- Check file paths (use absolute paths)
- Verify images exist in `assets/images/`
- Check file extensions (case-sensitive on Linux)

## 📈 Post-Deployment

### Monitor Performance

- Google PageSpeed Insights
- GTmetrix
- WebPageTest

### SEO

1. **Submit to Search Engines**
   - Google Search Console
   - Bing Webmaster Tools

2. **Generate Sitemap**
   - Automatically created at `/sitemap.xml`
   - Submit to search engines

3. **Social Media**
   - Share on LinkedIn, Twitter
   - Update profiles with website link

### Maintenance

Weekly:
- Check for broken links
- Monitor analytics
- Review form submissions

Monthly:
- Update dependencies
- Add new blog posts
- Review and update projects

## 🎯 Optimization Tips

### Images

```bash
# Optimize images before upload
# Use tools like:
- ImageOptim (Mac)
- Squoosh (Web)
- TinyPNG (Web)
```

### Fonts

- Use font-display: swap
- Preconnect to Google Fonts
- Consider self-hosting for best performance

### CSS/JS

- Automatically minified by Jekyll
- Consider critical CSS for above-the-fold

## 📞 Support

If you encounter issues:

1. Check GitHub Pages status: https://www.githubstatus.com/
2. Review Jekyll documentation: https://jekyllrb.com/docs/
3. Search GitHub issues: https://github.com/jekyll/jekyll/issues

## ✅ Final Checklist

Before going live:

- [ ] All personal info updated
- [ ] Profile photo added
- [ ] All project images added
- [ ] PWA icons generated
- [ ] Resume PDF uploaded
- [ ] Links tested (projects, social media)
- [ ] Mobile responsiveness verified
- [ ] Dark mode tested
- [ ] Blog posts reviewed
- [ ] SEO meta tags verified
- [ ] Performance tested (Lighthouse)
- [ ] Accessibility tested
- [ ] Cross-browser tested
- [ ] 404 page works
- [ ] Contact form configured (if using Formspree)

## 🎉 Launch!

Once everything is ready:

```bash
# Final commit
git add .
git commit -m "Ready for launch: Production-ready portfolio site"
git push

# Tag the release
git tag -a v1.0.0 -m "Initial release - Award-winning Jekyll portfolio"
git push --tags
```

Your award-winning portfolio is now live! 🚀

---

## Next Steps

- Add more blog posts regularly
- Update projects as you build them
- Collect testimonials
- Consider adding a newsletter
- Build case studies for top projects

**Need help?** Review the [README_JEKYLL.md](README_JEKYLL.md) for detailed documentation.
