document.addEventListener('DOMContentLoaded', function() {
    // Main upload section logic
    const chooseImageBtn = document.getElementById('chooseImage');
    const mainSampleImagesContainer = document.getElementById('mainSampleImagesContainer');
    const mainSampleImagesDiv = document.getElementById('mainSampleImages');
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imageInput = document.getElementById('imageInput');
    const makeProfessionalBtn = document.getElementById('makeProfessional');
    const preview = document.getElementById('preview');

    // Show sample images when "Choose Image" is clicked
    if (chooseImageBtn) chooseImageBtn.addEventListener('click', function() {
        mainSampleImagesContainer.style.display = 'block';
        chooseImageBtn.style.display = 'none';
    });

    // Handle upload image button
    if (uploadImageBtn) uploadImageBtn.addEventListener('click', function() {
        imageInput.click();
    });

    // Handle file input change
    if (imageInput) imageInput.addEventListener('change', function(event) {
        const files = event.target.files;
        preview.innerHTML = '';
        for (let i = 0; i < files.length; i++) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style = 'max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;';
                preview.appendChild(img);
            };
            reader.readAsDataURL(files[i]);
        }
        makeProfessionalBtn.style.display = 'inline-block';
    });

    // Populate main sample images
    if (mainSampleImagesDiv) {
        suggestedImageNames.forEach(name => {
            const img = document.createElement('img');
            img.src = `/static/img/${encodeURIComponent(name)}`;
            img.alt = 'Suggested';
            img.style = 'width:72px;height:72px;object-fit:cover;border-radius:0.6rem;box-shadow:0 2px 8px rgba(143,95,255,0.10);cursor:pointer;border:2px solid #eee;transition:box-shadow 0.2s,border 0.2s;';
            img.addEventListener('mouseenter',()=>{img.style.border='2px solid #8f5fff';img.style.boxShadow='0 2px 12px rgba(143,95,255,0.18)';});
            img.addEventListener('mouseleave',()=>{img.style.border='2px solid #eee';img.style.boxShadow='0 2px 8px rgba(143,95,255,0.10)';});
            img.addEventListener('click', async () => {
                // Set the sample image as the selected file
                const response = await fetch(img.src);
                const blob = await response.blob();
                const file = new File([blob], name, {type: blob.type});
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                imageInput.files = dataTransfer.files;
                
                // Show preview
                preview.innerHTML = '';
                const previewImg = document.createElement('img');
                previewImg.src = img.src;
                previewImg.style = 'max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;';
                preview.appendChild(previewImg);
                
                // Show make professional button
                makeProfessionalBtn.style.display = 'inline-block';
            });
            mainSampleImagesDiv.appendChild(img);
        });
    }

    // Handle form submission
    if (document.getElementById('uploadForm')) {
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const input = document.getElementById('imageInput');
            if (!input.files.length) return;
            const formData = new FormData();
            for (let i = 0; i < input.files.length; i++) {
                formData.append('images', input.files[i]);
            }
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                alert('Uploaded: ' + data.uploaded.join(', '));
            })
            .catch(() => alert('Upload failed.'));
        });
    }

    // Background Removal Modal logic
    const bgRemoveBtn = document.getElementById('bgRemoveBtn');
    const bgRemoveCard = document.getElementById('bgRemoveCard');
    const bgRemoveModal = document.getElementById('bgRemoveModal');
    const closeBgRemove = document.getElementById('closeBgRemove');
    const chooseBgRemove = document.getElementById('chooseBgRemove');
    const bgRemoveInput = document.getElementById('bgRemoveInput');
    const bgRemoveForm = document.getElementById('bgRemoveForm');
    const bgRemovePreview = document.getElementById('bgRemovePreview');
    const bgRemoveDownload = document.getElementById('bgRemoveDownload');

    function openBgRemoveModal() {
        bgRemoveModal.style.display = 'flex';
        bgRemovePreview.innerHTML = '';
        bgRemoveDownload.style.display = 'none';
    }
    function closeBgRemoveModal() {
        bgRemoveModal.style.display = 'none';
    }
    bgRemoveBtn.addEventListener('click', openBgRemoveModal);
    bgRemoveCard.addEventListener('click', openBgRemoveModal);
    closeBgRemove.addEventListener('click', closeBgRemoveModal);
    chooseBgRemove.addEventListener('click', () => bgRemoveInput.click());
    bgRemoveInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            bgRemovePreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = e.target.result;
            bgRemovePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });

    // Add loader element to the modal if not present
    if (!document.getElementById('bgRemoveLoader')) {
        const loader = document.createElement('div');
        loader.id = 'bgRemoveLoader';
        loader.style.display = 'none';
        loader.innerHTML = '<div class="spinner"></div><div style="margin-top:8px;color:#8f5fff;font-weight:600;">Processing...</div>';
        document.getElementById('bgRemovePreview').parentNode.insertBefore(loader, document.getElementById('bgRemovePreview'));
    }
    const bgRemoveLoader = document.getElementById('bgRemoveLoader');

    bgRemoveForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!bgRemoveInput.files.length) return ;
        const formData = new FormData();
        formData.append('image', bgRemoveInput.files[0]);
        // Show loader, hide preview and download
        bgRemoveLoader.style.display = 'flex';
        bgRemovePreview.style.display = 'none';
        bgRemoveDownload.style.display = 'none';
        fetch('/process/background_removal', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            bgRemoveLoader.style.display = 'none';
            bgRemovePreview.style.display = 'flex';
            if (data.processed_url) {
                bgRemovePreview.innerHTML = '';
                const img = document.createElement('img');
                img.src = data.processed_url + '?t=' + Date.now();
                bgRemovePreview.appendChild(img);
                bgRemoveDownload.href = data.processed_url;
                bgRemoveDownload.style.display = 'inline-block';
            } else {
                alert('Background removal failed.');
            }
        })
        .catch(() => {
            bgRemoveLoader.style.display = 'none';
            bgRemovePreview.style.display = 'flex';
            alert('Background removal failed.');
        });
    });

    // Make Professional logic
    if (document.getElementById('makeProfessional')) {
        document.getElementById('makeProfessional').addEventListener('click', function(e) {
            e.preventDefault();
            const input = document.getElementById('imageInput');
            if (!input.files.length) return alert('Please select an image.');
            const formData = new FormData();
            formData.append('image', input.files[0]);
            // Show loader, hide button and result card
            document.getElementById('makeProfessionalLoader').style.display = 'flex';
            document.getElementById('makeProfessional').style.display = 'none';
            document.getElementById('resultCard').style.display = 'none';
            fetch('/process/make_professional', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('makeProfessionalLoader').style.display = 'none';
                document.getElementById('makeProfessional').style.display = 'inline-block';
                if (data.processed_url) {
                    const card = document.getElementById('resultCard');
                    const img = document.getElementById('processedImg');
                    const dl = document.getElementById('downloadBtn');
                    img.src = data.processed_url + '?t=' + Date.now();
                    dl.href = data.processed_url;
                    dl.style.display = 'inline-block';
                    card.style.display = 'flex';
                } else {
                    alert('Processing failed.');
                }
            })
            .catch(() => {
                document.getElementById('makeProfessionalLoader').style.display = 'none';
                document.getElementById('makeProfessional').style.display = 'inline-block';
                alert('Processing failed.');
            });
        });
    }

    // Auto Enhancement logic
    if (document.getElementById('autoEnhanceBtn')) {
        document.getElementById('autoEnhanceBtn').addEventListener('click', function(e) {
            e.preventDefault();
            const input = document.getElementById('imageInput');
            if (!input.files.length) return;
            const formData = new FormData();
            formData.append('image', input.files[0]);
            // Show loader, hide button and result card
            document.getElementById('autoEnhanceLoader').style.display = 'flex';
            document.getElementById('autoEnhanceBtn').style.display = 'none';
            document.getElementById('enhanceResultCard').style.display = 'none';
            fetch('/process/enhance', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('autoEnhanceLoader').style.display = 'none';
                document.getElementById('autoEnhanceBtn').style.display = 'inline-block';
                if (data.processed_url) {
                    const card = document.getElementById('enhanceResultCard');
                    const img = document.getElementById('enhancedImg');
                    const dl = document.getElementById('enhanceDownloadBtn');
                    img.src = data.processed_url + '?t=' + Date.now();
                    dl.href = data.processed_url;
                    dl.style.display = 'inline-block';
                    card.style.display = 'flex';
                } else {
                    alert('Enhancement failed.');
                }
            })
            .catch(() => {
                document.getElementById('autoEnhanceLoader').style.display = 'none';
                document.getElementById('autoEnhanceBtn').style.display = 'inline-block';
                alert('Enhancement failed.');
            });
        });
    }
    // Also trigger enhancement when the feature card is clicked
    if (document.getElementById('autoEnhanceCard')) {
        document.getElementById('autoEnhanceCard').addEventListener('click', function() {
            document.getElementById('autoEnhanceBtn').click();
        });
    }

    // --- Auto Enhancement Modal Logic (Refactored) ---
    const autoEnhanceModal = document.getElementById('autoEnhanceModal');
    const openAutoEnhanceModalBtn = document.getElementById('autoEnhanceBtn');
    const openAutoEnhanceModalCard = document.getElementById('autoEnhanceCard');
    const closeAutoEnhanceModalBtn = document.getElementById('closeAutoEnhanceModal');
    const chooseAutoEnhanceModalBtn = document.getElementById('chooseAutoEnhanceModal');
    const autoEnhanceModalInput = document.getElementById('autoEnhanceModalInput');
    const autoEnhanceModalForm = document.getElementById('autoEnhanceModalForm');
    const autoEnhanceModalPreview = document.getElementById('autoEnhanceModalPreview');
    const autoEnhanceModalDownload = document.getElementById('autoEnhanceModalDownload');
    const suggestedEnhanceModalImagesDiv = document.getElementById('suggestedEnhanceModalImages');
    function openAutoEnhanceModal() {
        autoEnhanceModal.style.display = 'flex';
        autoEnhanceModalPreview.innerHTML = '';
        autoEnhanceModalDownload.style.display = 'none';
    }
    function closeAutoEnhanceModal() {
        autoEnhanceModal.style.display = 'none';
    }
    if (openAutoEnhanceModalBtn) openAutoEnhanceModalBtn.addEventListener('click', openAutoEnhanceModal);
    if (openAutoEnhanceModalCard) openAutoEnhanceModalCard.addEventListener('click', openAutoEnhanceModal);
    if (closeAutoEnhanceModalBtn) closeAutoEnhanceModalBtn.addEventListener('click', closeAutoEnhanceModal);
    if (chooseAutoEnhanceModalBtn) chooseAutoEnhanceModalBtn.addEventListener('click', () => autoEnhanceModalInput.click());
    if (autoEnhanceModalInput) autoEnhanceModalInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            autoEnhanceModalPreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = e.target.result;
            autoEnhanceModalPreview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
    if (suggestedEnhanceModalImagesDiv) {
        suggestedImageNames.forEach(name => {
            const img = document.createElement('img');
            img.src = `/static/img/${encodeURIComponent(name)}`;
            img.alt = 'Suggested';
            img.style = 'width:72px;height:72px;object-fit:cover;border-radius:0.6rem;box-shadow:0 2px 8px rgba(143,95,255,0.10);cursor:pointer;border:2px solid #eee;transition:box-shadow 0.2s,border 0.2s;';
            img.addEventListener('mouseenter',()=>{img.style.border='2px solid #8f5fff';img.style.boxShadow='0 2px 12px rgba(143,95,255,0.18)';});
            img.addEventListener('mouseleave',()=>{img.style.border='2px solid #eee';img.style.boxShadow='0 2px 8px rgba(143,95,255,0.10)';});
            img.addEventListener('click', async () => {
                const response = await fetch(img.src);
                const blob = await response.blob();
                const file = new File([blob], name, {type: blob.type});
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                autoEnhanceModalInput.files = dataTransfer.files;
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    autoEnhanceModalPreview.innerHTML = `<img src='${e.target.result}' style='max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;'/>`;
                };
                reader.readAsDataURL(file);
            });
            suggestedEnhanceModalImagesDiv.appendChild(img);
        });
    }
    if (autoEnhanceModalForm) autoEnhanceModalForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!autoEnhanceModalInput.files.length) return; // Silently do nothing if no image
        const formData = new FormData();
        formData.append('image', autoEnhanceModalInput.files[0]);
        autoEnhanceModalPreview.innerHTML = '<div class="spinner"></div><div style="margin-top:8px;color:#8f5fff;font-weight:600;">Enhancing...</div>';
        fetch('/process/enhance', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.processed_url) {
                autoEnhanceModalPreview.innerHTML = '';
                const img = document.createElement('img');
                img.src = data.processed_url + '?t=' + Date.now();
                autoEnhanceModalPreview.appendChild(img);
                autoEnhanceModalDownload.href = data.processed_url;
                autoEnhanceModalDownload.style.display = 'inline-block';
            } else {
                autoEnhanceModalPreview.innerHTML = 'Enhancement failed.';
            }
        })
        .catch(() => {
            autoEnhanceModalPreview.innerHTML = 'Enhancement failed.';
        });
    });

    // --- Creative Content Modal Logic (Refactored) ---
    const creativeContentModal = document.getElementById('creativeContentModal');
    const openCreativeContentModalBtn = document.getElementById('creativeContentBtn');
    const openCreativeContentModalCard = document.getElementById('creativeContentCard');
    const closeCreativeContentModalBtn = document.getElementById('closeCreativeContentModal');
    const chooseCreativeContentModalBtn = document.getElementById('chooseCreativeContentModal');
    const creativeContentModalInput = document.getElementById('creativeContentModalInput');
    const creativeContentModalForm = document.getElementById('creativeContentModalForm');
    const suggestedCreativeModalImagesDiv = document.getElementById('suggestedCreativeModalImages');
    const creativeContentModalLoader = document.getElementById('creativeContentModalLoader');
    const creativeContentModalResult = document.getElementById('creativeContentModalResult');
    const creativeContentModalHeading = document.getElementById('creativeContentModalHeading');
    const creativeContentModalDescription = document.getElementById('creativeContentModalDescription');
    const creativeContentModalAttributes = document.getElementById('creativeContentModalAttributes');
    function openCreativeContentModal() {
        creativeContentModal.style.display = 'flex';
        creativeContentModalLoader.style.display = 'none';
        creativeContentModalResult.style.display = 'none';
    }
    function closeCreativeContentModal() {
        creativeContentModal.style.display = 'none';
    }
    if (openCreativeContentModalBtn) openCreativeContentModalBtn.addEventListener('click', openCreativeContentModal);
    if (openCreativeContentModalCard) openCreativeContentModalCard.addEventListener('click', openCreativeContentModal);
    if (closeCreativeContentModalBtn) closeCreativeContentModalBtn.addEventListener('click', closeCreativeContentModal);
    if (chooseCreativeContentModalBtn) chooseCreativeContentModalBtn.addEventListener('click', () => creativeContentModalInput.click());
    if (creativeContentModalInput) creativeContentModalInput.addEventListener('change', function(event) {
        // Optionally show preview
    });
    if (suggestedCreativeModalImagesDiv) {
        suggestedImageNames.forEach(name => {
            const img = document.createElement('img');
            img.src = `/static/img/${encodeURIComponent(name)}`;
            img.alt = 'Suggested';
            img.style = 'width:72px;height:72px;object-fit:cover;border-radius:0.6rem;box-shadow:0 2px 8px rgba(143,95,255,0.10);cursor:pointer;border:2px solid #eee;transition:box-shadow 0.2s,border 0.2s;';
            img.addEventListener('mouseenter',()=>{img.style.border='2px solid #8f5fff';img.style.boxShadow='0 2px 12px rgba(143,95,255,0.18)';});
            img.addEventListener('mouseleave',()=>{
                if (!img.classList.contains('selected-sample-img')) {
                    img.style.border='2px solid #eee';
                    img.style.boxShadow='0 2px 8px rgba(143,95,255,0.10)';
                }
            });
            img.addEventListener('click', async () => {
                // Remove highlight from all
                Array.from(suggestedCreativeModalImagesDiv.children).forEach(child => child.classList.remove('selected-sample-img'));
                img.classList.add('selected-sample-img');
                // Set file input
                const response = await fetch(img.src);
                const blob = await response.blob();
                const file = new File([blob], name, {type: blob.type});
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                creativeContentModalInput.files = dataTransfer.files;
            });
            suggestedCreativeModalImagesDiv.appendChild(img);
        });
    }
    if (creativeContentModalForm) creativeContentModalForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!creativeContentModalInput.files.length) return; // Silently do nothing if no image
        const formData = new FormData();
        formData.append('image', creativeContentModalInput.files[0]);
        creativeContentModalLoader.style.display = 'flex';
        creativeContentModalResult.style.display = 'none';
        fetch('/process/creative_content', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            creativeContentModalLoader.style.display = 'none';
            if (data.title && data.description) {
                creativeContentModalHeading.textContent = data.title;
                creativeContentModalDescription.textContent = data.description;
                creativeContentModalAttributes.innerHTML = '';
                if (data.bullets) {
                    const ul = document.createElement('ul');
                    data.bullets.forEach(bullet => {
                        const li = document.createElement('li');
                        li.textContent = bullet;
                        ul.appendChild(li);
                    });
                    creativeContentModalAttributes.appendChild(ul);
                }
                if (data.tags) {
                    const tagsDiv = document.createElement('div');
                    tagsDiv.textContent = 'Tags: ' + data.tags.join(' ');
                    creativeContentModalAttributes.appendChild(tagsDiv);
                }
                if (data.caption) {
                    const captionDiv = document.createElement('div');
                    captionDiv.textContent = 'Caption: ' + data.caption;
                    creativeContentModalAttributes.appendChild(captionDiv);
                }
                creativeContentModalResult.style.display = 'block';
            } else {
                creativeContentModalHeading.textContent = '';
                creativeContentModalDescription.textContent = 'Could not generate content.';
                creativeContentModalAttributes.innerHTML = '';
                creativeContentModalResult.style.display = 'block';
            }
        })
        .catch(() => {
            creativeContentModalLoader.style.display = 'none';
            creativeContentModalHeading.textContent = '';
            creativeContentModalDescription.textContent = 'Could not generate content.';
            creativeContentModalAttributes.innerHTML = '';
            creativeContentModalResult.style.display = 'block';
        });
    });

    // --- Crop & Resize Modal Logic (Enhanced) ---
    const cropResizeModal = document.getElementById('cropResizeModal');
    const cropResizeCard = document.getElementById('cropResizeCard');
    const closeCropResize = document.getElementById('closeCropResize');
    const chooseCropResize = document.getElementById('chooseCropResize');
    const cropResizeInput = document.getElementById('cropResizeInput');
    const cropResizeForm = document.getElementById('cropResizeForm');
    const cropResizePreview = document.getElementById('cropResizePreview');
    const cropResizeLoader = document.getElementById('cropResizeLoader');
    const cropResizeResult = document.getElementById('cropResizeResult');
    const cropResizeImg = document.getElementById('cropResizeImg');
    const cropResizeDownload = document.getElementById('cropResizeDownload');
    const cropResizePlatform = document.getElementById('cropResizePlatform');
    const suggestedCropResizeImagesDiv = document.getElementById('suggestedCropResizeImages');

    function openCropResizeModal() {
        cropResizeModal.style.display = 'flex';
        cropResizeLoader.style.display = 'none';
        cropResizeResult.style.display = 'none';
        cropResizePreview.innerHTML = '';
    }
    function closeCropResizeModal() {
        cropResizeModal.style.display = 'none';
    }

    if (cropResizeCard) cropResizeCard.addEventListener('click', openCropResizeModal);
    if (closeCropResize) closeCropResize.addEventListener('click', closeCropResizeModal);
    if (chooseCropResize) chooseCropResize.addEventListener('click', () => cropResizeInput.click());

    if (cropResizeInput) cropResizeInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            cropResizePreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style = 'max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;';
            cropResizePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });

    if (suggestedCropResizeImagesDiv) {
        suggestedImageNames.forEach(name => {
            const img = document.createElement('img');
            img.src = `/static/img/${encodeURIComponent(name)}`;
            img.alt = 'Suggested';
            img.style = 'width:72px;height:72px;object-fit:cover;border-radius:0.6rem;box-shadow:0 2px 8px rgba(143,95,255,0.10);cursor:pointer;border:2px solid #eee;transition:box-shadow 0.2s,border 0.2s;';
            img.addEventListener('mouseenter',()=>{img.style.border='2px solid #8f5fff';img.style.boxShadow='0 2px 12px rgba(143,95,255,0.18)';});
            img.addEventListener('mouseleave',()=>{img.style.border='2px solid #eee';img.style.boxShadow='0 2px 8px rgba(143,95,255,0.10)';});
            img.addEventListener('click', async () => {
                const response = await fetch(img.src);
                const blob = await response.blob();
                const file = new File([blob], name, {type: blob.type});
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                cropResizeInput.files = dataTransfer.files;
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    cropResizePreview.innerHTML = `<img src='${e.target.result}' style='max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;'/>`;
                };
                reader.readAsDataURL(file);
            });
            suggestedCropResizeImagesDiv.appendChild(img);
        });
    }

    if (cropResizeForm) cropResizeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!cropResizeInput.files.length) return;
        const formData = new FormData();
        formData.append('image', cropResizeInput.files[0]);
        formData.append('platform', cropResizePlatform.value);
        cropResizeLoader.style.display = 'flex';
        cropResizeResult.style.display = 'none';
        fetch('/process/crop_resize', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            cropResizeLoader.style.display = 'none';
            if (data.processed_url) {
                cropResizeImg.src = data.processed_url + '?t=' + Date.now();
                cropResizeDownload.href = data.processed_url;
                cropResizeDownload.style.display = 'inline-block';
                cropResizeResult.style.display = 'block';
            } else {
                cropResizeResult.style.display = 'block';
                cropResizeImg.src = '';
                cropResizeDownload.style.display = 'none';
            }
        })
        .catch(() => {
            cropResizeLoader.style.display = 'none';
            cropResizeResult.style.display = 'block';
            cropResizeImg.src = '';
            cropResizeDownload.style.display = 'none';
        });
    });

    // Manual Crop logic for Crop & Resize Modal
    const manualCropBtn = document.getElementById('manualCropBtn');
    const manualCropModal = document.getElementById('manualCropModal');
    const manualCropImage = document.getElementById('manualCropImage');
    const confirmManualCrop = document.getElementById('confirmManualCrop');
    const cancelManualCrop = document.getElementById('cancelManualCrop');
    let cropper = null;

    if (manualCropBtn) manualCropBtn.addEventListener('click', function() {
        if (!cropResizeInput.files.length) return;
        // Show manual crop modal, hide main modal content
        cropResizeForm.style.display = 'none';
        cropResizeLoader.style.display = 'none';
        cropResizeResult.style.display = 'none';
        manualCropModal.style.display = 'flex';
        // Load image into cropper
        const file = cropResizeInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            manualCropImage.src = e.target.result;
            if (cropper) cropper.destroy();
            cropper = new Cropper(manualCropImage, {
                aspectRatio: 1024/1365,
                viewMode: 1,
                autoCropArea: 1,
                movable: true,
                zoomable: true,
                scalable: false,
                rotatable: false,
                responsive: true,
                background: false
            });
        };
        reader.readAsDataURL(file);
    });
    if (cancelManualCrop) cancelManualCrop.addEventListener('click', function() {
        manualCropModal.style.display = 'none';
        cropResizeForm.style.display = 'block';
        if (cropper) { cropper.destroy(); cropper = null; }
    });
    if (confirmManualCrop) confirmManualCrop.addEventListener('click', function() {
        if (!cropper) return;
        cropResizeLoader.style.display = 'flex';
        manualCropModal.style.display = 'none';
        cropper.getCroppedCanvas({width:1024, height:1365, imageSmoothingQuality:'high'}).toBlob(function(blob) {
            const formData = new FormData();
            formData.append('image', blob, 'cropped.png');
            formData.append('platform', 'meesho');
            fetch('/process/crop_resize', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                cropResizeLoader.style.display = 'none';
                if (data.processed_url) {
                    cropResizeImg.src = data.processed_url + '?t=' + Date.now();
                    cropResizeDownload.href = data.processed_url;
                    cropResizeDownload.style.display = 'inline-block';
                    cropResizeResult.style.display = 'block';
                } else {
                    cropResizeResult.style.display = 'block';
                    cropResizeImg.src = '';
                    cropResizeDownload.style.display = 'none';
                }
            })
            .catch(() => {
                cropResizeLoader.style.display = 'none';
                cropResizeResult.style.display = 'block';
                cropResizeImg.src = '';
                cropResizeDownload.style.display = 'none';
            });
            if (cropper) { cropper.destroy(); cropper = null; }
        }, 'image/png');
    });

    // --- Background Replacement Modal Logic (Enhanced) ---
    const bgReplaceModal = document.getElementById('bgReplaceModal');
    const bgReplaceCard = document.getElementById('bgReplaceCard');
    const closeBgReplace = document.getElementById('closeBgReplace');
    const chooseBgReplace = document.getElementById('chooseBgReplace');
    const bgReplaceInput = document.getElementById('bgReplaceInput');
    const bgReplaceForm = document.getElementById('bgReplaceForm');
    const bgReplacePreview = document.getElementById('bgReplacePreview');
    const bgReplacePicker = document.getElementById('bgReplacePicker');
    const bgReplaceLoader = document.getElementById('bgReplaceLoader');
    const bgReplaceResult = document.getElementById('bgReplaceResult');
    const bgReplaceImg = document.getElementById('bgReplaceImg');
    const bgReplaceDownload = document.getElementById('bgReplaceDownload');
    const suggestedBgReplaceImagesDiv = document.getElementById('suggestedBgReplaceImages');
    let selectedBg = null;

    function openBgReplaceModal() {
        bgReplaceModal.style.display = 'flex';
        bgReplaceLoader.style.display = 'none';
        bgReplaceResult.style.display = 'none';
        bgReplacePreview.innerHTML = '';
        
        // Hide the submit button initially
        const bgReplaceSubmit = document.getElementById('bgReplaceSubmit');
        if (bgReplaceSubmit) bgReplaceSubmit.style.display = 'none';
        
        // Load backgrounds
        const backgrounds = [
            {name: 'forest.jpg', label: 'Forest'},
            {name: 'golden.jpg', label: 'Golden'},
            {name: 'greenwaterdrops.jpg', label: 'Green Waterdrops'},
            {name: 'watersplash.jpg', label: 'Watersplash'},
            {name: 'white.jpg', label: 'White'}
        ];
        bgReplacePicker.innerHTML = '';
        backgrounds.forEach(bg => {
            const thumb = document.createElement('img');
            thumb.src = `/static/backgrounds/${bg.name}`;
            thumb.alt = bg.label;
            thumb.title = bg.label;
            thumb.style.width = '60px';
            thumb.style.height = '60px';
            thumb.style.objectFit = 'cover';
            thumb.style.borderRadius = '0.7rem';
            thumb.style.border = '2px solid #e0d6ff';
            thumb.style.cursor = 'pointer';
            thumb.style.boxShadow = '0 2px 8px #8f5fff11';
            thumb.style.transition = 'border 0.2s, box-shadow 0.2s';
            thumb.addEventListener('click', function() {
                selectedBg = bg.name;
                Array.from(bgReplacePicker.children).forEach(c => c.style.border = '2px solid #e0d6ff');
                thumb.style.border = '2px solid #8f5fff';
            });
            bgReplacePicker.appendChild(thumb);
        });
        selectedBg = backgrounds[0].name;
        bgReplacePicker.children[0].style.border = '2px solid #8f5fff';
    }

    function closeBgReplaceModal() {
        bgReplaceModal.style.display = 'none';
    }

    if (bgReplaceCard) bgReplaceCard.addEventListener('click', openBgReplaceModal);
    if (closeBgReplace) closeBgReplace.addEventListener('click', closeBgReplaceModal);
    if (chooseBgReplace) chooseBgReplace.addEventListener('click', () => bgReplaceInput.click());

    if (bgReplaceInput) bgReplaceInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            bgReplacePreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style = 'max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;';
            bgReplacePreview.appendChild(img);
            
            // Show the submit button when image is selected
            const bgReplaceSubmit = document.getElementById('bgReplaceSubmit');
            if (bgReplaceSubmit) bgReplaceSubmit.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
    });

    if (suggestedBgReplaceImagesDiv) {
        suggestedImageNames.forEach(name => {
            const img = document.createElement('img');
            img.src = `/static/img/${encodeURIComponent(name)}`;
            img.alt = 'Suggested';
            img.style = 'width:72px;height:72px;object-fit:cover;border-radius:0.6rem;box-shadow:0 2px 8px rgba(143,95,255,0.10);cursor:pointer;border:2px solid #eee;transition:box-shadow 0.2s,border 0.2s;';
            img.addEventListener('mouseenter',()=>{img.style.border='2px solid #8f5fff';img.style.boxShadow='0 2px 12px rgba(143,95,255,0.18)';});
            img.addEventListener('mouseleave',()=>{img.style.border='2px solid #eee';img.style.boxShadow='0 2px 8px rgba(143,95,255,0.10)';});
            img.addEventListener('click', async () => {
                const response = await fetch(img.src);
                const blob = await response.blob();
                const file = new File([blob], name, {type: blob.type});
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                bgReplaceInput.files = dataTransfer.files;
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    bgReplacePreview.innerHTML = `<img src='${e.target.result}' style='max-width:180px;max-height:180px;border-radius:0.6rem;margin-top:0.7rem;'/>`;
                    
                    // Show the submit button when sample image is selected
                    const bgReplaceSubmit = document.getElementById('bgReplaceSubmit');
                    if (bgReplaceSubmit) bgReplaceSubmit.style.display = 'inline-block';
                };
                reader.readAsDataURL(file);
            });
            suggestedBgReplaceImagesDiv.appendChild(img);
        });
    }

    if (bgReplaceForm) bgReplaceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!bgReplaceInput.files.length) return;
        console.log('Background replacement form submitted');
        console.log('Selected background:', selectedBg);
        const formData = new FormData();
        formData.append('image', bgReplaceInput.files[0]);
        formData.append('background', selectedBg);
        bgReplaceLoader.style.display = 'flex';
        bgReplaceResult.style.display = 'none';
        fetch('/process/replace_background', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            console.log('Background replacement response:', data);
            bgReplaceLoader.style.display = 'none';
            if (data.processed_url) {
                bgReplaceImg.src = data.processed_url + '?t=' + Date.now();
                bgReplaceDownload.href = data.processed_url;
                bgReplaceDownload.style.display = 'inline-block';
                bgReplaceResult.style.display = 'block';
                
                // Auto-scroll to the result
                setTimeout(() => {
                    bgReplaceResult.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 100);
            } else {
                bgReplaceResult.style.display = 'block';
                bgReplaceImg.src = '';
                bgReplaceDownload.style.display = 'none';
                
                // Auto-scroll to the result even if failed
                setTimeout(() => {
                    bgReplaceResult.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 100);
            }
        })
        .catch((error) => {
            console.error('Background replacement error:', error);
            bgReplaceLoader.style.display = 'none';
            bgReplaceResult.style.display = 'block';
            bgReplaceImg.src = '';
            bgReplaceDownload.style.display = 'none';
        });
    });

    // Typewriter effect for yellow text
    const typewriterText = "e-commerce sellers & solo founders";
    const typewriterEl = document.getElementById('typewriter-highlight');
    if (typewriterEl) {
        typewriterEl.innerHTML = ""; // Clear any existing text
        typewriterEl.style.color = "#ffd47a";
        typewriterEl.style.fontWeight = "700";
        typewriterEl.style.fontStyle = "italic";
        let i = 0;
        function typeWriter() {
            if (i < typewriterText.length) {
                typewriterEl.innerHTML += typewriterText.charAt(i);
                i++;
                setTimeout(typeWriter, 140); // Slower speed (ms per character)
            } else {
                setTimeout(() => {
                    typewriterEl.innerHTML = "";
                    i = 0;
                    setTimeout(typeWriter, 400); // Short pause before restarting
                }, 1000); // Wait 1s before clearing and restarting
            }
        }
        typeWriter();
    }

    // Enable smooth scroll for anchor links
    document.documentElement.style.scrollBehavior = 'smooth';
    // Optional: Smooth scroll for a scroll-down button
    const scrollDownBtn = document.getElementById('scrollDownBtn');
    if (scrollDownBtn) {
        scrollDownBtn.addEventListener('click', function() {
            // Scroll to the next section after hero
            const nextSection = document.querySelector('.upload-section, .features, section');
            if (nextSection) {
                nextSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    // Smooth scroll for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').slice(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}); 