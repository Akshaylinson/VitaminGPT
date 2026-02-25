function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`${tab}-section`).classList.add('active');
}

document.getElementById('image-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('image-preview').innerHTML = 
                `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('patient_id', document.getElementById('patient-id').value);
    formData.append('name', document.getElementById('patient-name').value);
    formData.append('address', document.getElementById('patient-address').value);
    formData.append('phone', document.getElementById('patient-phone').value);
    formData.append('image', document.getElementById('image-file').files[0]);
    
    document.getElementById('loading').style.display = 'flex';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        if (data.error) {
            displayError(data.error);
        } else {
            displayResult(data.result);
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        displayError('An error occurred during analysis: ' + error.message);
    }
});

function displayResult(result) {
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    
    let vitaminsHtml = result.vitamin_deficiencies.map(v => `
        <div class="vitamin-item">
            <h4>${v.vitamin}</h4>
            <p>${v.reason}</p>
            <div class="food-list">
                ${v.recommended_foods.map(f => `<span class="food-tag">${f}</span>`).join('')}
            </div>
        </div>
    `).join('');
    
    resultContent.innerHTML = `
        <div class="result-card">
            <h3>Detected Condition</h3>
            <div class="disease-tag">${result.detected_disease}</div>
            <p class="confidence">Confidence: ${(result.confidence_score * 100).toFixed(1)}%</p>
            
            <h3 style="margin-top: 20px;">Possible Vitamin Deficiencies</h3>
            ${vitaminsHtml}
            
            <p style="margin-top: 20px; color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px;">
                ⚠️ This is an indicative analysis for educational purposes only. Consult a healthcare professional.
            </p>
        </div>
    `;
    
    resultSection.style.display = 'block';
}

function displayError(message) {
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    
    resultContent.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${message}
        </div>
    `;
    
    resultSection.style.display = 'block';
}

async function loadPatientReports() {
    const patientId = document.getElementById('patient-lookup-id').value;
    
    if (!patientId) {
        alert('Please enter a Patient ID');
        return;
    }
    
    try {
        const response = await fetch(`/api/patient/${patientId}/reports`);
        const data = await response.json();
        
        if (response.status === 404) {
            document.getElementById('patient-reports').innerHTML = 
                '<div class="error">Patient not found</div>';
            return;
        }
        
        displayPatientReports(data);
    } catch (error) {
        document.getElementById('patient-reports').innerHTML = 
            `<div class="error">Error loading reports: ${error.message}</div>`;
    }
}

function displayPatientReports(data) {
    const reportsDiv = document.getElementById('patient-reports');
    
    if (data.reports.length === 0) {
        reportsDiv.innerHTML = '<p>No reports found for this patient.</p>';
        return;
    }
    
    let html = `
        <div class="result-card">
            <h3>Patient Information</h3>
            <p><strong>Name:</strong> ${data.patient.name}</p>
            <p><strong>ID:</strong> ${data.patient.id}</p>
            <p><strong>Phone:</strong> ${data.patient.phone || 'N/A'}</p>
        </div>
        <h3>Medical Reports</h3>
    `;
    
    data.reports.forEach(report => {
        const vitaminsHtml = report.vitamin_data.map(v => `
            <div class="vitamin-item">
                <h4>${v.vitamin}</h4>
                <p>${v.reason}</p>
                <div class="food-list">
                    ${v.recommended_foods.map(f => `<span class="food-tag">${f}</span>`).join('')}
                </div>
            </div>
        `).join('');
        
        html += `
            <div class="report-card">
                <p><strong>Date:</strong> ${new Date(report.created_at).toLocaleString()}</p>
                <div class="disease-tag">${report.detected_disease}</div>
                <p class="confidence">Confidence: ${(report.confidence_score * 100).toFixed(1)}%</p>
                <h4 style="margin-top: 15px;">Vitamin Deficiencies:</h4>
                ${vitaminsHtml}
            </div>
        `;
    });
    
    reportsDiv.innerHTML = html;
}
