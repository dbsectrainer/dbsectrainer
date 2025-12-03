# dbsectrainer Portfolio - Jekyll Site

## Award-Winning Jekyll Portfolio Site

This is a modern, award-winning Jekyll portfolio site featuring:

- **Glassmorphism Design**: Modern UI with glass-effect cards
- **Dark Mode**: Automatic theme switching with localStorage persistence
- **Progressive Web App**: Offline functionality with service worker
- **Responsive Design**: Mobile-first, works on all devices
- **Animations**: Smooth scroll animations with AOS library
- **SEO Optimized**: Jekyll SEO tag integration
- **Performance**: Lighthouse score 90+ target

## 🚀 Quick Start

### Prerequisites

- Ruby 3.0+
- Bundler
- Jekyll 4.3+

### Installation

```bash
# Install dependencies
bundle install

# Start development server
bundle exec jekyll serve

# Build for production
bundle exec jekyll build
```

The site will be available at `http://localhost:4000`

## 📁 Project Structure

```
├── _config.yml              # Site configuration
├── _data/                   # Data files (skills, navigation, social)
├── _includes/              # Reusable components
│   ├── head.html
│   ├── header.html
│   ├── footer.html
│   ├── project-card.html
│   ├── blog-card.html
│   └── skill-bar.html
├── _layouts/               # Page templates
│   ├── default.html
│   ├── home.html
│   ├── page.html
│   ├── post.html
│   ├── project.html
│   └── case-study.html
├── _projects/              # Project collection
├── _posts/                 # Blog posts
├── _pages/                 # Static pages
├── _sass/                  # SCSS partials
│   ├── _variables.scss
│   ├── _base.scss
│   ├── _animations.scss
│   ├── _components.scss
│   ├── _layout.scss
│   └── _syntax.scss
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── files/
├── manifest.json           # PWA manifest
├── sw.js                   # Service worker
└── index.html              # Homepage
```

## 🎨 Features

### Modern Design
- Glassmorphism effects
- Gradient animations
- Smooth transitions
- Custom CSS properties
- Dark mode support

### Performance
- Lazy loading images
- Minified CSS/JS
- Service worker caching
- Optimized assets
- Fast page loads

### Accessibility
- WCAG 2.1 AA compliant
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

### SEO
- Jekyll SEO tag
- Open Graph tags
- Twitter cards
- Sitemap generation
- RSS feed

## 🛠️ Customization

### Update Site Information

Edit `_config.yml`:

```yaml
title: Your Name | Your Title
email: your.email@example.com
description: Your bio
author:
  name: Your Name
  title: Your Title
  bio: Your professional bio
```

### Add Projects

Create a new file in `_projects/`:

```markdown
---
title: "Project Name"
tagline: "Short description"
layout: project
featured: true
order: 1
category: ai-ml
tech_stack:
  - Python
  - TensorFlow
---

## Project content here
```

### Add Blog Posts

Create a new file in `_posts/`:

```markdown
---
layout: post
title: "Post Title"
date: 2024-12-02 10:00:00 -0000
tags: [AI, Security]
excerpt: "Short excerpt"
---

## Post content here
```

### Customize Colors

Edit `_sass/_variables.scss`:

```scss
:root {
  --primary-600: #your-color;
  --secondary-600: #your-color;
  --accent-600: #your-color;
}
```

## 📱 PWA Setup

The site is configured as a Progressive Web App. To customize:

1. Update `manifest.json` with your information
2. Add app icons in `assets/images/icons/`
3. Customize `sw.js` caching strategy

## 🚀 Deployment

### GitHub Pages

1. Push to GitHub repository
2. Go to Settings → Pages
3. Select branch: `main`, folder: `/`
4. Save and wait for deployment

Your site will be live at `https://username.github.io`

### Custom Domain

1. Add `CNAME` file with your domain
2. Configure DNS settings
3. Enable HTTPS in GitHub Pages settings

## 📊 Analytics

To add Google Analytics:

1. Uncomment in `_config.yml`:
```yaml
google_analytics: UA-XXXXXXXXX-X
```

## 🔧 Development

### Local Development

```bash
# Watch for changes
bundle exec jekyll serve --livereload

# Draft posts
bundle exec jekyll serve --drafts

# Future posts
bundle exec jekyll serve --future
```

### Build Production

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

## 🎯 Performance Optimization

- Images: Use WebP format, optimize before upload
- CSS: Minified automatically
- JS: Minified in production
- Fonts: Preconnect to Google Fonts
- Caching: Service worker handles offline

## 📝 Content Guidelines

### Projects
- Include screenshots/images
- Add live demo links
- Explain problem, solution, impact
- List technologies used
- Show code samples

### Blog Posts
- Use proper heading hierarchy
- Add code syntax highlighting
- Include images/diagrams
- Add tags for categorization
- Write engaging excerpts

## 🐛 Troubleshooting

### Build Errors

```bash
# Clear cache
bundle exec jekyll clean

# Update dependencies
bundle update

# Rebuild
bundle exec jekyll build
```

### Service Worker Issues

Clear browser cache and hard reload (`Cmd+Shift+R` or `Ctrl+Shift+F5`)

## 📚 Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages](https://docs.github.com/en/pages)
- [PWA Guide](https://web.dev/progressive-web-apps/)
- [Liquid Syntax](https://shopify.github.io/liquid/)

## 🤝 Contributing

This is a personal portfolio, but feel free to fork and adapt for your own use!

## 📄 License

MIT License - feel free to use this template for your own portfolio.

## 👤 Author

**dbsectrainer**
- GitHub: [@dbsectrainer](https://github.com/dbsectrainer)
- LinkedIn: [dbsectrainer](https://linkedin.com/in/dbsectrainer)

---

Built with ❤️ using Jekyll, modern CSS, and vanilla JavaScript.
