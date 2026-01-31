/**
 * "Who Said It?" Game Logic
 * Interactive engagement feature for Holt Bot
 */

// Game State
let currentAnswer = null;
let correctCount = 0;
let incorrectCount = 0;
let characters = [];

// DOM Elements
const quoteText = document.getElementById('quote-text');
const episodeName = document.getElementById('episode-name');
const guessInput = document.getElementById('guess');
const submitBtn = document.getElementById('submit-btn');
const nextBtn = document.getElementById('next-btn');
const resultDiv = document.getElementById('result');
const autocompleteList = document.getElementById('autocomplete-list');
const correctCountEl = document.getElementById('correct-count');
const incorrectCountEl = document.getElementById('incorrect-count');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCharacters();
    loadNewQuote();
    setupEventListeners();
});

// Load character list for autocomplete
async function loadCharacters() {
    try {
        const response = await fetch('/game/characters');
        const data = await response.json();
        characters = data.characters || [];
    } catch (error) {
        console.error('Failed to load characters:', error);
        characters = ['Jake', 'Amy', 'Rosa', 'Charles', 'Captain Holt', 'Sergeant Jeffords', 'Gina', 'Hitchcock', 'Scully'];
    }
}

// Load a new quote
async function loadNewQuote() {
    quoteText.textContent = 'Loading quote...';
    episodeName.textContent = 'Loading...';
    guessInput.value = '';
    guessInput.disabled = false;
    submitBtn.disabled = false;
    nextBtn.classList.add('hidden');
    resultDiv.classList.add('hidden');
    currentAnswer = null;

    try {
        const response = await fetch('/game/quote');
        const data = await response.json();

        if (data.error) {
            quoteText.textContent = data.error;
            return;
        }

        quoteText.textContent = `"${data.text}"`;
        episodeName.textContent = data.episode;
        currentAnswer = data.answer;
    } catch (error) {
        console.error('Failed to load quote:', error);
        quoteText.textContent = 'Failed to load quote. Please try again.';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Submit answer
    submitBtn.addEventListener('click', submitAnswer);
    guessInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitAnswer();
    });

    // Next quote
    nextBtn.addEventListener('click', loadNewQuote);

    // Autocomplete
    guessInput.addEventListener('input', handleAutocomplete);
    guessInput.addEventListener('focus', handleAutocomplete);
    document.addEventListener('click', (e) => {
        if (!guessInput.contains(e.target) && !autocompleteList.contains(e.target)) {
            autocompleteList.classList.add('hidden');
        }
    });

    // Search
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(handleSearch, 300);
    });
}

// Handle autocomplete
function handleAutocomplete() {
    const value = guessInput.value.toLowerCase().trim();
    
    if (!value) {
        autocompleteList.classList.add('hidden');
        return;
    }

    const matches = characters.filter(c => 
        c.toLowerCase().includes(value)
    );

    if (matches.length === 0) {
        autocompleteList.classList.add('hidden');
        return;
    }

    autocompleteList.innerHTML = matches.map(c => `
        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer text-gray-700" data-character="${c}">
            ${c}
        </div>
    `).join('');

    autocompleteList.classList.remove('hidden');

    // Add click handlers
    autocompleteList.querySelectorAll('[data-character]').forEach(el => {
        el.addEventListener('click', () => {
            guessInput.value = el.dataset.character;
            autocompleteList.classList.add('hidden');
        });
    });
}

// Submit answer
async function submitAnswer() {
    const guess = guessInput.value.trim();
    
    if (!guess || !currentAnswer) return;

    submitBtn.disabled = true;
    guessInput.disabled = true;

    try {
        const response = await fetch(`/game/verify?guess=${encodeURIComponent(guess)}&answer=${encodeURIComponent(currentAnswer)}`, {
            method: 'POST'
        });
        const data = await response.json();

        // Update score
        if (data.correct) {
            correctCount++;
            resultDiv.className = 'mt-6 p-4 rounded-lg bg-green-50 border border-green-200';
        } else {
            incorrectCount++;
            resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-50 border border-red-200';
        }

        correctCountEl.textContent = correctCount;
        incorrectCountEl.textContent = incorrectCount;

        // Show result
        resultDiv.innerHTML = `
            <p class="${data.correct ? 'text-green-800' : 'text-red-800'} font-semibold">
                ${data.message}
            </p>
        `;
        resultDiv.classList.remove('hidden');
        nextBtn.classList.remove('hidden');

    } catch (error) {
        console.error('Failed to verify answer:', error);
        resultDiv.innerHTML = '<p class="text-red-800">Error verifying answer. Please try again.</p>';
        resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-50 border border-red-200';
        resultDiv.classList.remove('hidden');
        submitBtn.disabled = false;
        guessInput.disabled = false;
    }
}

// Handle quote search
async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (query.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch(`/game/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.quotes && data.quotes.length > 0) {
            searchResults.innerHTML = data.quotes.map(q => `
                <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <p class="text-gray-700 italic">"${q.text}"</p>
                    <p class="text-sm text-gray-500 mt-2">
                        <span class="font-semibold">${q.character}</span> • ${q.episode}
                    </p>
                </div>
            `).join('');
            searchResults.classList.remove('hidden');
        } else {
            searchResults.innerHTML = '<p class="text-gray-500 text-center py-4">No quotes found.</p>';
            searchResults.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Search failed:', error);
        searchResults.innerHTML = '<p class="text-red-500 text-center py-4">Search failed. Please try again.</p>';
        searchResults.classList.remove('hidden');
    }
}
