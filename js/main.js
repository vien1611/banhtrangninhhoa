/**
 * BÁNH TRÁNG THỦ CÔNG LÂM THANH — NINH HÒA
 * INTERACTIVE ENGINE: 2-IMAGE HERO SLIDER, DYNAMIC DB SYNC & DIRECT CONTACT
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. HERO INFINITE CAROUSEL SLIDER (LƯỚT ẢNH XƯỞNG BÁNH QUAY VÒNG VÔ HẠN)
  const carouselTrack = document.getElementById('heroCarouselTrack');
  const prevBtn = document.getElementById('heroPrevBtn');
  const nextBtn = document.getElementById('heroNextBtn');
  const carouselContainer = document.querySelector('.hero-carousel');

  if (carouselTrack) {
    const originalSlides = Array.from(carouselTrack.children);
    const totalOriginalSlides = originalSlides.length;

    // Clone first and last slide for seamless infinite looping
    const firstClone = originalSlides[0].cloneNode(true);
    const lastClone = originalSlides[totalOriginalSlides - 1].cloneNode(true);

    firstClone.classList.add('clone');
    lastClone.classList.add('clone');

    carouselTrack.appendChild(firstClone);
    carouselTrack.insertBefore(lastClone, originalSlides[0]);

    // Current index in track: 1 is the first original slide
    let currentIndex = 1;
    let isTransitioning = false;
    let autoSlideTimer = null;
    const transitionStyle = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';

    // Set initial position without transition
    carouselTrack.style.transition = 'none';
    carouselTrack.style.transform = `translateX(-${currentIndex * 100}%)`;

    function updateDots() {
      const activeDotIndex = (currentIndex - 1 + totalOriginalSlides) % totalOriginalSlides;
      const dots = document.querySelectorAll('.carousel-dot');
      dots.forEach((dot, idx) => {
        dot.classList.toggle('active', idx === activeDotIndex);
      });
    }

    function moveToSlide(index) {
      if (isTransitioning) return;
      isTransitioning = true;
      currentIndex = index;
      carouselTrack.style.transition = transitionStyle;
      carouselTrack.style.transform = `translateX(-${currentIndex * 100}%)`;
      updateDots();
    }

    // Handle seamless jump when reaching cloned edges
    carouselTrack.addEventListener('transitionend', () => {
      isTransitioning = false;
      if (currentIndex === totalOriginalSlides + 1) {
        // Reached firstClone at end -> jump invisibly to original first slide
        carouselTrack.style.transition = 'none';
        currentIndex = 1;
        carouselTrack.style.transform = `translateX(-${currentIndex * 100}%)`;
      } else if (currentIndex === 0) {
        // Reached lastClone at start -> jump invisibly to original last slide
        carouselTrack.style.transition = 'none';
        currentIndex = totalOriginalSlides;
        carouselTrack.style.transform = `translateX(-${currentIndex * 100}%)`;
      }
    });

    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.preventDefault();
        moveToSlide(currentIndex + 1);
        resetAutoSlide();
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.preventDefault();
        moveToSlide(currentIndex - 1);
        resetAutoSlide();
      });
    }

    // Indicator Dots click
    document.querySelectorAll('.carousel-dot').forEach(dot => {
      dot.addEventListener('click', (e) => {
        const targetIndex = parseInt(e.target.dataset.slide, 10);
        moveToSlide(targetIndex + 1);
        resetAutoSlide();
      });
    });

    // Touch Swipe for Mobile
    let touchStartX = 0;
    let touchEndX = 0;

    if (carouselContainer) {
      carouselContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      carouselContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
      }, { passive: true });

      carouselContainer.addEventListener('mouseenter', () => clearInterval(autoSlideTimer));
      carouselContainer.addEventListener('mouseleave', () => startAutoSlide());
    }

    function handleSwipe() {
      if (touchEndX < touchStartX - 40) {
        moveToSlide(currentIndex + 1);
        resetAutoSlide();
      } else if (touchEndX > touchStartX + 40) {
        moveToSlide(currentIndex - 1);
        resetAutoSlide();
      }
    }

    function startAutoSlide() {
      clearInterval(autoSlideTimer);
      autoSlideTimer = setInterval(() => {
        moveToSlide(currentIndex + 1);
      }, 4000);
    }

    function resetAutoSlide() {
      clearInterval(autoSlideTimer);
      startAutoSlide();
    }

    startAutoSlide();
  }

  // 2. DYNAMIC DATABASE FETCH FOR PRODUCTS (FROM SQLite API)
  const productGrid = document.getElementById('productGrid');

  async function syncProductsFromDB() {
    if (!productGrid) return;
    try {
      const res = await fetch('/api/products');
      if (!res.ok) return;
      const json = await res.json();
      if (json.success && Array.isArray(json.data) && json.data.length > 0) {
        renderProductCards(json.data);
      }
    } catch (err) {
      // Graceful fallback to static pre-rendered cards in HTML
      // Console log for debug only
    }
  }

  function renderProductCards(products) {
    productGrid.innerHTML = '';
    products.forEach(prod => {
      const article = document.createElement('article');
      article.className = 'product-card';

      const badgeHtml = prod.badge 
        ? `<div class="product-badge-flag ${prod.badge_type === 'accent' ? 'accent' : ''}">${prod.badge}</div>`
        : '';

      const specTagHtml = prod.spec_tag 
        ? `<span class="product-spec-tag">${prod.spec_tag}</span>`
        : '';

      article.innerHTML = `
        ${badgeHtml}
        <div class="product-image-container">
          <img 
            src="${prod.image_url}" 
            alt="${prod.name}" 
            width="400" 
            height="500" 
            loading="lazy" 
            decoding="async"
            onerror="this.src='picture/banhram1.jpg'"
          >
        </div>
        <div class="product-details">
          <div class="product-spec-row">
            ${specTagHtml}
            <span class="product-stars">★★★★★</span>
          </div>
          <h3 class="product-name">${prod.name}</h3>
          <p class="product-desc">${prod.description}</p>
          <div class="product-footer">
            <span class="product-delivery-note">${prod.delivery_note || 'Đóng thùng chống ẩm'}</span>
            <button type="button" class="btn-contact-item" data-product-name="${prod.name}" aria-label="Liên hệ trực tiếp ${prod.name}">
              <span>Liên hệ trực tiếp</span>
            </button>
          </div>
        </div>
      `;
      productGrid.appendChild(article);
    });

    bindContactButtons();
  }

  // 3. CONTACT DROPDOWN TOGGLE (For Mobile & Touch Support)
  const contactDropdownWrap = document.getElementById('contactDropdownWrap');
  const contactTriggerBtn = document.getElementById('contactTriggerBtn');

  if (contactTriggerBtn && contactDropdownWrap) {
    contactTriggerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      contactDropdownWrap.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!contactDropdownWrap.contains(e.target)) {
        contactDropdownWrap.classList.remove('open');
      }
    });
  }

  // 4. TOAST NOTIFICATION UTILITY
  const toastMsg = document.getElementById('toastMsg');
  const toastText = document.getElementById('toastText');

  function showToast(message) {
    if (!toastMsg) return;
    toastText.textContent = message;
    toastMsg.classList.add('show');
    setTimeout(() => {
      toastMsg.classList.remove('show');
    }, 3200);
  }

  // 5. PRODUCT BUTTONS "LIÊN HỆ TRỰC TIẾP"
  function bindContactButtons() {
    document.querySelectorAll('.btn-contact-item').forEach(btn => {
      btn.onclick = () => {
        const productName = btn.dataset.productName || 'Đặc sản Bánh Tráng';
        showToast(`Đã chọn "${productName}". Mời quý khách kết nối Chị Thanh hoặc Anh Lâm bên dưới!`);
        const contactSection = document.getElementById('lien-he');
        if (contactSection) {
          contactSection.scrollIntoView({ behavior: 'smooth' });
        }
      };
    });
  }

  bindContactButtons();

  // 6. REVIEWS STAR FILTER (1-5 SAO)
  const reviewFilterBtns = document.querySelectorAll('.review-filter-btn');
  const reviewCards = document.querySelectorAll('.review-card');

  if (reviewFilterBtns.length > 0) {
    reviewFilterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        reviewFilterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filterVal = btn.dataset.filter;

        reviewCards.forEach(card => {
          if (filterVal === 'all' || card.dataset.rating === filterVal) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // 7. MOBILE NAVIGATION MENU
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.querySelector('.nav-links');
  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
      const isExpanded = navLinks.style.display === 'flex';
      navLinks.style.display = isExpanded ? 'none' : 'flex';
      if (!isExpanded) {
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = 'var(--header-h)';
        navLinks.style.left = '0';
        navLinks.style.right = '0';
        navLinks.style.backgroundColor = 'var(--bg-primary)';
        navLinks.style.padding = '20px';
        navLinks.style.borderBottom = '1px solid var(--border-light)';
        navLinks.style.boxShadow = 'var(--shadow-hover)';
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 860) {
          navLinks.style.display = 'none';
        }
      });
    });
  }

  // Attempt to sync products from SQLite API
  syncProductsFromDB();
});
