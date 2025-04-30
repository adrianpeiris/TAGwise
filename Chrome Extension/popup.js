document.addEventListener('DOMContentLoaded', async () => {
    const urlInput = document.getElementById('urlInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const errorMessage = document.getElementById('errorMessage');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');

    // Hide loading and results on startup
    loading.style.display = 'none';
    results.style.display = 'none';

    // Get the current tab's URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        urlInput.value = currentTab.url;
    });

    analyzeButton.addEventListener('click', async () => {
        errorMessage.style.display = 'none';
        results.style.display = 'none';
        loading.style.display = 'block';

        try {
            const backendUrl = 'http://127.0.0.1:5000/predict'; // Ensure this URL is correct
            console.log('Sending request to:', backendUrl); // Debugging log
            console.log('Request body:', { url: urlInput.value }); // Debugging log

            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: urlInput.value })
            });

            console.log('Response status:', response.status); // Debugging log

            if (!response.ok) {
                throw new Error('Unable to fetch data. Please check the URL or try again later.');
            }

            const data = await response.json();
            console.log('Response data:', data); // Debugging log

            if (data.status === 'success') {
                updateResults(data);
                results.style.display = 'block';
            } else {
                throw new Error('Unable to analyze the URL. Please try a different one.');
            }
        } catch (error) {
            console.error('Error during fetch:', error); // Debugging log
            errorMessage.textContent = 'Error: Unable to process the request. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    });

    const saveButton = document.getElementById('saveButton');
    saveButton.addEventListener('click', async () => {
        const results = {
            url: document.getElementById('urlInput').value,
            title: document.getElementById('title').textContent,
            site_name: document.getElementById('siteName').textContent,
            category: document.getElementById('categorySelect').value,
            tags: document.getElementById('tagsInput').value.split(',').map(tag => tag.trim()),
            content: document.getElementById('content').textContent,
            favicon_url: document.getElementById('favicon').src
        };

        try {
            const response = await fetch('http://127.0.0.1:5000/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(results)
            });

            const data = await response.json();

            if (data.status === 'success') {
                alert('Content saved successfully!');
            } else if (data.status === 'duplicate') {
                alert('This link is already saved.');
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error saving content:', error);
            alert(`Error: ${error.message}`);
        }
    });

    const exploreButton = document.getElementById('exploreButton');
    exploreButton.addEventListener('click', () => {
        window.open('http://127.0.0.1:5000/explore', '_blank');
    });

    function updateResults(data) {
        // Update UI elements with prediction data
        document.getElementById('favicon').src = data.favicon_url || 'default-icon.png';
        document.getElementById('title').textContent = data.title;
        document.getElementById('siteName').textContent = data.site_name;
        document.getElementById('categorySelect').value = data.category;
        document.getElementById('tagsContainer').innerHTML = data.tags.map(tag => 
            `<div class="tag">${tag} <button type="button" onclick="removeTag('${tag}')">✕</button></div>`
        ).join('');
        document.getElementById('tagsInput').value = data.tags.join(',');
        document.getElementById('visitLink').href = data.url;
        document.getElementById('content').textContent = data.content;
    }

    function addTag() {
        const newTagInput = document.getElementById('newTagInput');
        const tagsContainer = document.getElementById('tagsContainer');
        const tagsInput = document.getElementById('tagsInput');
        const newTag = newTagInput.value.trim();

        if (newTag) {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag';
            tagElement.innerHTML = `
                ${newTag} 
                <button type="button" class="remove-tag-button" data-tag="${newTag}">✕</button>
            `;
            tagsContainer.appendChild(tagElement);

            const currentTags = tagsInput.value ? tagsInput.value.split(',') : [];
            currentTags.push(newTag);
            tagsInput.value = currentTags.join(',');

            newTagInput.value = '';
        }

        // Attach event listener to the remove button
        attachRemoveTagListeners();
    }

    function removeTag(tag) {
        const tagsContainer = document.getElementById('tagsContainer');
        const tagsInput = document.getElementById('tagsInput');
        const currentTags = tagsInput.value.split(',').filter(t => t !== tag);

        tagsInput.value = currentTags.join(',');
        tagsContainer.innerHTML = '';
        currentTags.forEach(t => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag';
            tagElement.innerHTML = `
                ${t} 
                <button type="button" class="remove-tag-button" data-tag="${t}">✕</button>
            `;
            tagsContainer.appendChild(tagElement);
        });

        // Reattach event listeners to the updated remove buttons
        attachRemoveTagListeners();
    }

    function attachRemoveTagListeners() {
        const removeTagButtons = document.querySelectorAll('.remove-tag-button');
        removeTagButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tag = e.target.getAttribute('data-tag');
                removeTag(tag);
            });
        });
    }

    // Attach event listener to the "Add Tag" button
    const addTagButton = document.getElementById('addTagButton');
    addTagButton.addEventListener('click', addTag);
});
