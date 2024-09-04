document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const results = document.getElementById('results');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('file', document.getElementById('fileInput').files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                generateVisualizations(data.filename);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    function generateVisualizations(filename) {
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: filename,
                instrument: document.getElementById('instrumentSelect').value,
                plotType: document.getElementById('plotTypeSelect').value,
                binSize: document.getElementById('binSizeInput').value
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                displayResults(data);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function displayResults(data) {
        results.innerHTML = '<h2 class="text-xl font-bold mb-4">Results:</h2>';
        data.plotFiles.forEach(file => {
            results.innerHTML += `<p class="mb-2"><a href="/output/${data.outputDir}/${file}" target="_blank" class="text-blue-500 hover:text-blue-700">${file}</a></p>`;
        });
    }
});
