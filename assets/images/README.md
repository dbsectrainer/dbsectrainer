# Images Directory

This directory contains all images for the Jekyll site.

## Directory Structure

```
assets/images/
├── icons/              # PWA app icons
│   ├── icon-72x72.png
│   ├── icon-96x96.png
│   ├── icon-128x128.png
│   ├── icon-144x144.png
│   ├── icon-152x152.png
│   ├── icon-192x192.png
│   ├── icon-384x384.png
│   └── icon-512x512.png
├── projects/           # Project screenshots
│   ├── global-ai-dashboard.png
│   ├── mandarin-pathways.png
│   ├── enterprise-checklists.png
│   ├── cloud-security.png
│   └── security-scanner.png
├── profile/           # Profile photos
│   └── profile.jpg    # 300x300px recommended
├── blog/              # Blog post images
│   ├── zero-trust-ml.jpg
│   └── ai-security.jpg
└── screenshots/       # PWA screenshots
    ├── desktop.png    # 1280x720px
    └── mobile.png     # 750x1334px
```

## Image Guidelines

### Profile Photo
- Size: 300x300px (square)
- Format: JPG or PNG
- Professional headshot
- Good lighting, neutral background

### Project Images
- Size: 1200x630px (recommended)
- Format: PNG or JPG
- Show key features/UI
- Include branding if applicable

### Blog Images
- Size: 1200x630px
- Format: JPG
- Relevant to article content
- High quality, optimized

### PWA Icons
- Sizes: 72, 96, 128, 144, 152, 192, 384, 512px
- Format: PNG
- Square with padding
- Transparent or solid background

## Optimization

Before adding images:

1. **Compress**:
   - Use TinyPNG, Squoosh, or ImageOptim
   - Target: <200KB for photos, <50KB for icons

2. **Format**:
   - Photos: JPG (quality 80-85)
   - Graphics/logos: PNG
   - Consider WebP for better compression

3. **Responsive**:
   - Provide multiple sizes if needed
   - Use `srcset` for responsive images

## Adding Images

1. Place image in appropriate directory
2. Reference in markdown/HTML:
   ```markdown
   ![Alt text](/assets/images/projects/my-project.png)
   ```

3. Or in frontmatter:
   ```yaml
   image: /assets/images/projects/my-project.png
   ```

## Placeholder Images

Until you add your images, the site will work without them. Add images to enhance visual appeal and professionalism.

## Tools

- [TinyPNG](https://tinypng.com/) - Image compression
- [Squoosh](https://squoosh.app/) - Image optimizer
- [PWA Asset Generator](https://www.pwabuilder.com/) - Generate PWA icons
- [Canva](https://www.canva.com/) - Create blog images
