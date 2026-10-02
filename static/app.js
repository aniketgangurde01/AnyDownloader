document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const extractForm = document.getElementById('extract-form');
  const urlInput = document.getElementById('url-input');
  const pasteBtn = document.getElementById('paste-btn');
  const clearBtn = document.getElementById('clear-btn');
  const submitBtn = document.getElementById('submit-btn');
  const loadingSpinner = document.getElementById('loading-spinner');
  const platformIcon = document.getElementById('platform-icon');
  const noticeBox = document.getElementById('notice-box');
  const noticeTitle = document.getElementById('notice-title');
  const noticeMessage = document.getElementById('notice-message');
  const resultsSection = document.getElementById('results-section');

  // Media Overview elements
  const mediaThumb = document.getElementById('media-thumb');
  const mediaDuration = document.getElementById('media-duration');
  const mediaSource = document.getElementById('media-source');
  const mediaUploader = document.getElementById('media-uploader');
  const mediaTitle = document.getElementById('media-title');
  const mediaViews = document.getElementById('media-views');
  const viewsText = document.getElementById('views-text');
  const mediaLink = document.getElementById('media-link');

  // Tabs & Grids
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const videoGrid = document.getElementById('video-grid');
  const audioGrid = document.getElementById('audio-grid');
  const videoCount = document.getElementById('video-count');
  const audioCount = document.getElementById('audio-count');

  // Modal elements
  const downloadModal = document.getElementById('download-modal');
  const modalHeading = document.getElementById('modal-heading');
  const modalSubtext = document.getElementById('modal-subtext');
  const modalDot = document.getElementById('modal-dot');
  const progressBar = document.getElementById('progress-bar');
  const progressPercent = document.getElementById('progress-percent');
  const progressSpeed = document.getElementById('progress-speed');
  const progressEta = document.getElementById('progress-eta');
  const step1 = document.getElementById('step-1');
  const step2 = document.getElementById('step-2');
  const step3 = document.getElementById('step-3');
  const readyActionBox = document.getElementById('ready-action-box');
  const readyFilename = document.getElementById('ready-filename');
  const readyFilesize = document.getElementById('ready-filesize');
  const directDownloadBtn = document.getElementById('direct-download-btn');

  // Platforms Catalog container
  const platformsCatalog = document.getElementById('platforms-catalog');

  let currentMediaData = null;
  let activePollInterval = null;

  // Icons SVG map for auto-detection
  const platformIcons = {
    youtube: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#FF0000"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`,
    instagram: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#E1306C"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    facebook: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`,
    tiktok: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#FE2C55"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.24 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>`,
    twitter: `<svg viewBox="0 0 24 24" width="20" height="20" fill="#1DA1F2"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    terabox: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#00A4FF"><path d="M21 16.5c0 .83-.67 1.5-1.5 1.5h-15c-.83 0-1.5-.67-1.5-1.5v-9c0-.83.67-1.5 1.5-1.5h15c.83 0 1.5.67 1.5 1.5v9zM6 9h12v2H6V9zm0 4h8v2H6v-2z"/></svg>`,
    default: `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>`
  };

  // URL input detector
  function updatePlatformIcon(url) {
    const u = url.toLowerCase();
    let iconKey = 'default';
    if (u.includes('youtube.com') || u.includes('youtu.be')) iconKey = 'youtube';
    else if (u.includes('instagram.com')) iconKey = 'instagram';
    else if (u.includes('facebook.com') || u.includes('fb.watch') || u.includes('fb.com')) iconKey = 'facebook';
    else if (u.includes('tiktok.com')) iconKey = 'tiktok';
    else if (u.includes('twitter.com') || u.includes('://x.com') || u.includes('.x.com') || u.includes('/x.com')) iconKey = 'twitter';
    else if (u.includes('terabox.com') || u.includes('1024tera') || u.includes('teraboxapp') || u.includes('mirrobox')) iconKey = 'terabox';

    platformIcon.innerHTML = platformIcons[iconKey] || platformIcons.default;
    platformIcon.classList.toggle('active', iconKey !== 'default');
    clearBtn.classList.toggle('hidden', url.length === 0);
  }

  urlInput.addEventListener('input', (e) => {
    updatePlatformIcon(e.target.value.trim());
  });

  // Paste from clipboard
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        updatePlatformIcon(urlInput.value);
        urlInput.focus();
        showNotice('Link Pasted!', 'Click "Extract Streams" or press Enter to analyze.', false);
      }
    } catch (err) {
      urlInput.focus();
    }
  });

  // Clear button
  clearBtn.addEventListener('click', () => {
    urlInput.value = '';
    updatePlatformIcon('');
    clearBtn.classList.add('hidden');
    urlInput.focus();
  });

  // Quick platform tag clicks
  document.querySelectorAll('.platform-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      const domain = tag.getAttribute('data-domain');
      urlInput.placeholder = `Paste ${domain} link here...`;
      urlInput.focus();
    });
  });

  // Tab switching
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add('active');
    });
  });

  // Notice helper
  window.showNotice = function(title, message, isError = true) {
    noticeTitle.textContent = title;
    noticeMessage.textContent = message;
    noticeBox.classList.remove('hidden');
    noticeBox.classList.toggle('info', !isError);
  };

  window.closeNotice = function() {
    noticeBox.classList.add('hidden');
  };

  // Extraction Ticker & Quick Actions
  const extractStatusTicker = document.getElementById('extract-status-ticker');
  const tickerText = document.getElementById('ticker-text');
  const quickBestVideoBtn = document.getElementById('quick-best-video-btn');
  const quickBestAudioBtn = document.getElementById('quick-best-audio-btn');
  const quickBestRes = document.getElementById('quick-best-res');

  let tickerInterval = null;

  function startExtractionTicker() {
    extractStatusTicker.classList.remove('hidden');
    const stages = [
      "⚡ Contacting media servers...",
      "🔍 Probing audio & video streams...",
      "✨ Decoding resolutions and bitrates...",
      "🚀 Organizing download presets..."
    ];
    let idx = 0;
    tickerText.textContent = stages[0];
    tickerInterval = setInterval(() => {
      idx = (idx + 1) % stages.length;
      tickerText.textContent = stages[idx];
    }, 900);
  }

  function stopExtractionTicker() {
    if (tickerInterval) clearInterval(tickerInterval);
    extractStatusTicker.classList.add('hidden');
  }

  // Form submission / Extraction
  extractForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (!url) return;

    closeNotice();

    // Check client sessionStorage cache for instant 0ms render
    try {
      const cached = sessionStorage.getItem('omni_cache_' + url);
      if (cached) {
        const parsed = JSON.parse(cached);
        currentMediaData = parsed;
        renderResults(parsed);
        showNotice('Instant Cache Hit', 'Loaded from instant session cache.', false);
        return;
      }
    } catch (_) {}

    submitBtn.disabled = true;
    loadingSpinner.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    startExtractionTicker();

    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        showNotice(data.error || 'Notice', data.message || 'Could not process this URL.', true);
        return;
      }

      currentMediaData = data;
      try {
        sessionStorage.setItem('omni_cache_' + url, JSON.stringify(data));
      } catch (_) {}

      renderResults(data);

    } catch (err) {
      showNotice('Connection Error', 'Failed to communicate with extraction server. Check your connection.', true);
    } finally {
      stopExtractionTicker();
      submitBtn.disabled = false;
      loadingSpinner.classList.add('hidden');
    }
  });

  // Render extracted media
  function renderResults(data) {
    mediaThumb.src = data.thumbnail || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80';
    mediaDuration.textContent = data.duration || '00:00';
    mediaSource.textContent = data.platform.name;
    mediaUploader.textContent = data.uploader || 'Creator';
    mediaTitle.textContent = data.title;
    
    if (data.view_count) {
      viewsText.textContent = `${data.view_count} views`;
      mediaViews.classList.remove('hidden');
    } else {
      mediaViews.classList.add('hidden');
    }

    mediaLink.href = data.webpage_url;

    // Configure 1-Click Instant Action Buttons
    const videoFormats = data.video_formats || [];
    if (videoFormats.length > 0) {
      const topVideo = videoFormats[0];
      quickBestRes.textContent = topVideo.resolution;
      quickBestVideoBtn.onclick = () => {
        startDownload('video', topVideo.format_id, topVideo.resolution, 'mp4', `${topVideo.resolution} MP4`);
      };
      quickBestVideoBtn.style.display = 'inline-flex';
    } else {
      quickBestVideoBtn.style.display = 'none';
    }

    quickBestAudioBtn.onclick = () => {
      startDownload('audio', null, null, 'mp3', 'Studio MP3 (320kbps)', '320');
    };

    // Render Video Qualities
    videoGrid.innerHTML = '';
    videoCount.textContent = videoFormats.length;

    if (videoFormats.length === 0) {
      videoGrid.innerHTML = `<div class="empty-state"><p>No dedicated video resolutions detected for this source. Try extracting as audio.</p></div>`;
    } else {
      videoFormats.forEach((vf, idx) => {
        const card = document.createElement('div');
        const isFeatured = idx === 0 || vf.height >= 1080;
        card.className = `quality-card ${isFeatured ? 'featured' : ''}`;

        let badgeClass = 'res-badge';
        if (vf.height >= 2160) badgeClass += ' uhd';
        else if (vf.height >= 1080) badgeClass += ' fhd';

        card.innerHTML = `
          <div>
            <div class="quality-header">
              <span class="res-title">
                ${vf.resolution}
                ${vf.fps ? `<span style="font-size:0.75rem; color:var(--text-muted); font-weight:600;">${vf.fps}</span>` : ''}
              </span>
              <span class="${badgeClass}">${vf.quality_badge}</span>
            </div>
            <div class="quality-meta" style="margin-top: 8px;">
              <span>MP4 Format</span>
              <span class="filesize-tag">~${vf.filesize}</span>
            </div>
          </div>
          <button type="button" class="download-action-btn" onclick="startDownload('video', '${vf.format_id}', '${vf.resolution}', 'mp4', '${vf.resolution} MP4')">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>Download ${vf.resolution}</span>
          </button>
        `;
        videoGrid.appendChild(card);
      });
    }

    // Render Audio Presets
    audioGrid.innerHTML = '';
    const audioFormats = data.audio_formats || [];
    audioCount.textContent = audioFormats.length;

    audioFormats.forEach(af => {
      const card = document.createElement('div');
      card.className = `quality-card ${af.recommended ? 'featured' : ''}`;
      
      card.innerHTML = `
        <div>
          <div class="quality-header">
            <span class="res-title">${af.name}</span>
            <span class="res-badge ${af.recommended ? 'fhd' : ''}">${af.quality_badge}</span>
          </div>
          <div class="quality-meta" style="margin-top: 8px;">
            <span>${af.bitrate}</span>
            <span class="filesize-tag">${af.ext.toUpperCase()}</span>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;">${af.description}</p>
        </div>
        <button type="button" class="download-action-btn" onclick="startDownload('audio', null, null, '${af.ext}', '${af.name}', '${af.id.includes('320') ? '320' : (af.id.includes('256') ? '256' : (af.id.includes('192') ? '192' : '128'))}')">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none">
            <path d="M9 18V5l12-2v13"></path>
            <circle cx="6" cy="18" r="3"></circle>
            <circle cx="18" cy="16" r="3"></circle>
          </svg>
          <span>Extract ${af.ext.toUpperCase()}</span>
        </button>
      `;
      audioGrid.appendChild(card);
    });

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Start Download trigger
  window.startDownload = async function(mediaType, formatId, resolution, ext, label, audioQuality = '320') {
    if (!currentMediaData) return;

    openModal(label);

    const payload = {
      url: currentMediaData.webpage_url,
      media_type: mediaType,
      format_id: formatId,
      resolution: resolution,
      ext: ext,
      audio_quality: audioQuality
    };

    try {
      const response = await fetch('/api/download/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const res = await response.json();
      if (res.success && res.job_id) {
        pollJobProgress(res.job_id);
      } else {
        setModalError(res.detail || 'Could not queue the download task.');
      }
    } catch (err) {
      setModalError('Failed to initiate stream processing.');
    }
  };

  // Poll Job Progress
  function pollJobProgress(jobId) {
    if (activePollInterval) clearInterval(activePollInterval);

    activePollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/download/status/${jobId}`);
        if (!response.ok) {
          clearInterval(activePollInterval);
          setModalError('Stream job session lost.');
          return;
        }

        const data = await response.json();

        if (data.status === 'downloading') {
          updateModalProgress(data.progress, data.speed, data.eta, 1);
        } else if (data.status === 'processing') {
          updateModalProgress(99, 'FFmpeg merging audio & video...', 'Almost ready', 2);
        } else if (data.status === 'finished') {
          clearInterval(activePollInterval);
          setModalReady(jobId, data.filename, data.file_size);
        } else if (data.status === 'error') {
          clearInterval(activePollInterval);
          setModalError(data.error || 'Extraction process failed.');
        }
      } catch (e) {
        // Continue polling on transient errors
      }
    }, 700);
  }

  function openModal(label) {
    modalHeading.textContent = `Processing ${label}`;
    modalSubtext.textContent = 'Contacting source servers and acquiring video streams...';
    modalDot.className = 'status-indicator-dot';
    progressBar.style.width = '5%';
    progressPercent.textContent = '0%';
    progressSpeed.textContent = 'Connecting...';
    progressEta.textContent = 'Estimating...';

    step1.className = 'step-item active';
    step2.className = 'step-item';
    step3.className = 'step-item';

    readyActionBox.classList.add('hidden');
    downloadModal.classList.remove('hidden');
  }

  function updateModalProgress(pct, speed, eta, step) {
    progressBar.style.width = `${Math.max(5, pct)}%`;
    progressPercent.textContent = `${Math.round(pct)}%`;
    progressSpeed.textContent = speed || 'Processing...';
    progressEta.textContent = eta || 'A few moments';

    if (step >= 1) {
      step1.className = 'step-item done';
      step2.className = 'step-item active';
    }
    if (step >= 2) {
      step2.className = 'step-item active';
    }
  }

  function setModalReady(jobId, filename, filesize) {
    progressBar.style.width = '100%';
    progressPercent.textContent = '100%';
    progressSpeed.textContent = 'Complete';
    progressEta.textContent = 'Ready';

    step1.className = 'step-item done';
    step2.className = 'step-item done';
    step3.className = 'step-item done';

    modalDot.className = 'status-indicator-dot success';
    modalHeading.textContent = 'Stream Ready to Save';
    modalSubtext.textContent = 'Media stream merged with high fidelity audio and converted successfully.';

    readyFilename.textContent = filename || 'downloaded_media.mp4';
    readyFilesize.textContent = filesize ? `Approx ${filesize}` : 'Ready for device';
    directDownloadBtn.href = `/api/download/file/${jobId}`;

    readyActionBox.classList.remove('hidden');
  }

  function setModalError(errorMsg) {
    modalDot.className = 'status-indicator-dot error';
    modalHeading.textContent = 'Processing Failed';
    modalSubtext.textContent = errorMsg;
    progressSpeed.textContent = 'Stopped';
    progressEta.textContent = 'Failed';
  }

  window.closeModal = function() {
    if (activePollInterval) clearInterval(activePollInterval);
    downloadModal.classList.add('hidden');
  };

  // Load Supported Platforms Catalog
  async function loadPlatformsCatalog() {
    try {
      const res = await fetch('/api/supported-platforms');
      const data = await res.json();
      platformsCatalog.innerHTML = '';

      data.categories.forEach(cat => {
        const catCard = document.createElement('div');
        catCard.className = 'catalog-category';

        let itemsHtml = '';
        cat.items.forEach(item => {
          itemsHtml += `
            <div class="catalog-item">
              <div class="catalog-item-info">
                <span class="catalog-name">${item.name}</span>
                <span class="catalog-desc">${item.desc}</span>
              </div>
              <span class="catalog-pill ${!item.supported ? 'warn' : ''}">${item.badge}</span>
            </div>
          `;
        });

        catCard.innerHTML = `
          <h3 class="category-title">${cat.name}</h3>
          <div class="category-items">
            ${itemsHtml}
          </div>
        `;
        platformsCatalog.appendChild(catCard);
      });
    } catch (e) {
      console.error('Failed to load platforms catalog', e);
    }
  }

  loadPlatformsCatalog();
});
