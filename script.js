const ESD_CLASSES = [
    'Psoriasis',
    'Seborrheic Dermatitis', 
    'Lichen Planus',
    'Pityriasis Rosea',
    'Chronic Dermatitis',
    'Pityriasis Rubra Pilaris'
];

class ESDClassifier {
    constructor() {
        this.form = document.getElementById('esdForm');
        this.classifyBtn = document.getElementById('classifyBtn');
        this.btnText = document.getElementById('btnText');
        this.btnLoader = document.getElementById('btnLoader');
        this.resultsCard = document.getElementById('resultsCard');
        this.predictedClass = document.getElementById('predictedClass');
        this.confidence = document.getElementById('confidence');
        this.probabilityList = document.getElementById('probabilityList');
        this.toast = document.getElementById('toast');
        
        this.predictors = {
            itching: 0,
            koebnerPhenomenon: 0,
            follicularPapules: 0,
            fibrosisOfPapillaryDermis: 0,
            spongiosis: 0,
            inflammatoryMononuclearInfiltrate: 0,
            bandLikeInfiltrate: 0,
            age: 30
        };
        
        this.init();
    }
    
    init() {
        this.classifyBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleClassify();
        });

        const inputs = this.form.querySelectorAll('select, input');
        inputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const field = e.target.name;
                const value = field === 'age' ? parseFloat(e.target.value) || 0 : parseInt(e.target.value) || 0;
                this.predictors[field] = value;
            });
        });
    }
    
    validateForm() {
        const inputs = this.form.querySelectorAll('select[required], input[required]');
        for (let input of inputs) {
            if (!input.value || input.value === '') {
                this.showToast('Please fill in all required fields', 'error');
                return false;
            }
        }
        return true;
    }
    
    async handleClassify() {
        if (!this.validateForm()) {
            return;
        }
        
        this.setLoading(true);
        
        try {
            // Send the predictors to the backend for classification
            const response = await fetch('https://esd-classification-system.onrender.com/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.predictors),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const result = await response.json();
            this.displayResults(result);
            this.showToast(
                `Classification Complete: ${result.predictedClass} (${(result.confidence * 100).toFixed(1)}% confidence)`,
                'success'
            );
        } catch (error) {
            console.error('Classification failed:', error);
            this.showToast('Classification failed. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    // The rest of the display and utility functions remain the same
    displayResults(result) {
        this.predictedClass.textContent = result.predictedClass;
        this.confidence.textContent = `Confidence: ${(result.confidence * 100).toFixed(1)}%`;
        
        const sortedProbs = Object.entries(result.probabilities)
            .sort(([,a], [,b]) => b - a);
        
        this.probabilityList.innerHTML = '';
        
        sortedProbs.forEach(([className, probability]) => {
            const item = document.createElement('div');
            item.className = 'flex justify-between items-center';
            
            item.innerHTML = `
                <span class="text-sm">${className}</span>
                <div class="flex items-center gap-2">
                    <div class="w-24 h-2 bg-muted rounded-full overflow-hidden">
                        <div class="h-full bg-primary transition-all duration-500" style="width: ${probability * 100}%"></div>
                    </div>
                    <span class="text-sm w-12 text-right">${(probability * 100).toFixed(1)}%</span>
                </div>
            `;
            
            this.probabilityList.appendChild(item);
        });
        
        this.resultsCard.classList.remove('hidden');
        this.resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    setLoading(isLoading) {
        if (isLoading) {
            this.classifyBtn.disabled = true;
            this.btnText.classList.add('hidden');
            this.btnLoader.classList.remove('hidden');
        } else {
            this.classifyBtn.disabled = false;
            this.btnText.classList.remove('hidden');
            this.btnLoader.classList.add('hidden');
        }
    }
    
    showToast(message, type = 'success') {
        this.toast.textContent = message;
        this.toast.className = `toast ${type}`;
        this.toast.classList.remove('hidden');
        
        setTimeout(() => {
            this.toast.classList.add('hidden');
        }, 4000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ESDClassifier();
});
