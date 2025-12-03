// ====================================
// Main JavaScript
// Theme switching, mobile menu, smooth scroll, etc.
// ====================================

(function() {
  'use strict';

  // ==================
  // Theme Toggle
  // ==================

  const themeToggle = document.querySelector('.theme-toggle');
  const html = document.documentElement;

  // Initialize theme from localStorage or system preference
  const savedTheme = localStorage.getItem('theme');
  const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  const currentTheme = savedTheme || systemPreference;

  html.setAttribute('data-theme', currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';

      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);

      // Add animation class
      themeToggle.style.transform = 'rotate(360deg)';
      setTimeout(() => {
        themeToggle.style.transform = '';
      }, 300);
    });
  }

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      const newTheme = e.matches ? 'dark' : 'light';
      html.setAttribute('data-theme', newTheme);
    }
  });

  // ==================
  // Mobile Menu Toggle
  // ==================

  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navbarMenu = document.querySelector('.navbar-menu');

  if (mobileMenuToggle && navbarMenu) {
    mobileMenuToggle.addEventListener('click', () => {
      const isExpanded = mobileMenuToggle.getAttribute('aria-expanded') === 'true';

      mobileMenuToggle.setAttribute('aria-expanded', !isExpanded);
      navbarMenu.classList.toggle('active');

      // Prevent body scroll when menu is open
      document.body.style.overflow = isExpanded ? '' : 'hidden';
    });

    // Close menu when clicking nav links
    const navLinks = navbarMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        navbarMenu.classList.remove('active');
        document.body.style.overflow = '';
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!navbarMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        navbarMenu.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // ==================
  // Back to Top Button
  // ==================

  const backToTopButton = document.querySelector('.back-to-top');

  if (backToTopButton) {
    // Show/hide button based on scroll position
    const toggleBackToTop = () => {
      if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
      } else {
        backToTopButton.classList.remove('visible');
      }
    };

    window.addEventListener('scroll', toggleBackToTop);
    toggleBackToTop(); // Initial check

    // Scroll to top on click
    backToTopButton.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // ==================
  // Smooth Scroll for Anchor Links
  // ==================

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');

      // Skip if it's just "#"
      if (href === '#') return;

      const target = document.querySelector(href);

      if (target) {
        e.preventDefault();

        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        // Update URL without jumping
        if (history.pushState) {
          history.pushState(null, null, href);
        }
      }
    });
  });

  // ==================
  // Active Navigation Link
  // ==================

  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const highlightNavigation = () => {
    const scrollPosition = window.pageYOffset + 100;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      const sectionId = section.getAttribute('id');

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  };

  if (sections.length > 0 && navLinks.length > 0) {
    window.addEventListener('scroll', highlightNavigation);
    highlightNavigation(); // Initial check
  }

  // ==================
  // Lazy Loading Images
  // ==================

  if ('loading' in HTMLImageElement.prototype) {
    // Browser supports native lazy loading
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
      img.src = img.src;
    });
  } else {
    // Fallback for browsers that don't support lazy loading
    const images = document.querySelectorAll('img[loading="lazy"]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src || img.src;
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });

    images.forEach(img => imageObserver.observe(img));
  }

  // ==================
  // Copy Code Button
  // ==================

  const codeBlocks = document.querySelectorAll('pre code');

  codeBlocks.forEach(codeBlock => {
    const pre = codeBlock.parentElement;

    // Create copy button
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-code-button';
    copyButton.textContent = 'Copy';
    copyButton.setAttribute('aria-label', 'Copy code to clipboard');

    // Add button to pre element
    pre.style.position = 'relative';
    pre.appendChild(copyButton);

    copyButton.addEventListener('click', async () => {
      const code = codeBlock.textContent;

      try {
        await navigator.clipboard.writeText(code);
        copyButton.textContent = 'Copied!';
        copyButton.classList.add('copied');

        setTimeout(() => {
          copyButton.textContent = 'Copy';
          copyButton.classList.remove('copied');
        }, 2000);
      } catch (err) {
        console.error('Failed to copy code:', err);
        copyButton.textContent = 'Error';

        setTimeout(() => {
          copyButton.textContent = 'Copy';
        }, 2000);
      }
    });
  });

  // ==================
  // Form Validation (if contact form exists)
  // ==================

  const contactForm = document.querySelector('.contact-form');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      // Get form data
      const formData = new FormData(contactForm);
      const data = Object.fromEntries(formData);

      // Basic validation
      if (!data.name || !data.email || !data.message) {
        alert('Please fill in all required fields.');
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.email)) {
        alert('Please enter a valid email address.');
        return;
      }

      // If validation passes, you can submit the form
      // For now, we'll just log the data
      console.log('Form data:', data);

      // Show success message
      const successMessage = document.createElement('div');
      successMessage.className = 'form-success';
      successMessage.textContent = 'Thank you for your message! I will get back to you soon.';
      contactForm.appendChild(successMessage);

      // Reset form
      contactForm.reset();

      // Remove success message after 5 seconds
      setTimeout(() => {
        successMessage.remove();
      }, 5000);
    });
  }

  // ==================
  // Skill Bar Animation on Scroll
  // ==================

  const skillBars = document.querySelectorAll('.skill-progress');

  if (skillBars.length > 0) {
    const skillObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'skillFill 1.5s ease-out forwards';
          skillObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.5
    });

    skillBars.forEach(bar => skillObserver.observe(bar));
  }

  // ==================
  // External Links (open in new tab)
  // ==================

  const externalLinks = document.querySelectorAll('a[href^="http"]');

  externalLinks.forEach(link => {
    // Skip if it's an internal link
    if (link.hostname === window.location.hostname) return;

    // Add target and rel attributes
    if (!link.hasAttribute('target')) {
      link.setAttribute('target', '_blank');
    }
    if (!link.hasAttribute('rel')) {
      link.setAttribute('rel', 'noopener noreferrer');
    }

    // Add external link icon (optional)
    if (!link.querySelector('svg')) {
      const icon = document.createElement('span');
      icon.innerHTML = ' ↗';
      icon.style.fontSize = '0.8em';
      link.appendChild(icon);
    }
  });

  // ==================
  // Reading Time Estimator (for blog posts)
  // ==================

  const postContent = document.querySelector('.post-content .content-wrapper');

  if (postContent) {
    const text = postContent.textContent;
    const wordCount = text.trim().split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / 180); // 180 words per minute

    // Update reading time display if it exists
    const readingTimeElement = document.querySelector('.post-reading-time');
    if (readingTimeElement) {
      readingTimeElement.textContent = `${readingTime} min read`;
    }
  }

  // ==================
  // Performance Optimization
  // ==================

  // Debounce function for scroll events
  const debounce = (func, wait = 10) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  // Apply debounce to scroll events
  if (backToTopButton) {
    const debouncedToggle = debounce(() => {
      if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
      } else {
        backToTopButton.classList.remove('visible');
      }
    }, 10);

    window.addEventListener('scroll', debouncedToggle);
  }

  // ==================
  // Console Easter Egg
  // ==================

  console.log(
    '%c👋 Welcome to my portfolio!',
    'font-size: 20px; font-weight: bold; color: #2563eb;'
  );
  console.log(
    '%cInterested in the code? Check out the source on GitHub!',
    'font-size: 14px; color: #6b7280;'
  );
  console.log(
    '%c🔐 Specializing in AI/ML Security',
    'font-size: 14px; color: #10b981;'
  );

  // ==================
  // Initialize
  // ==================

  console.log('✓ Site initialized successfully');

})();
