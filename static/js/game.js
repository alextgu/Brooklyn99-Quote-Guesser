/**
 * "Who Said It?" Game Logic
 * Brooklyn 99 Quote Guesser
 */

// Game State
let currentAnswer = null;
let currentEpisode = null;
let currentSeason = null;
let currentStreak = 0;
let bestStreak = 0;
let characters = [];
let episodesBySeason = {};

// DOM Elements
const quoteText = document.getElementById('quote-text');
const guessInput = document.getElementById('guess');
const guessSeason = document.getElementById('guess-season');
const guessEpisode = document.getElementById('guess-episode');
const submitBtn = document.getElementById('submit-btn');
const nextBtn = document.getElementById('next-btn');
const resultDiv = document.getElementById('result');
const autocompleteList = document.getElementById('autocomplete-list');
const streakCountEl = document.getElementById('streak-count');
const bestStreakEl = document.getElementById('best-streak');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCharacters();
    loadEpisodes();
    loadStreakFromStorage();
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

// Load streak from localStorage
function loadStreakFromStorage() {
    currentStreak = parseInt(localStorage.getItem('holt_streak') || '0', 10);
    bestStreak = parseInt(localStorage.getItem('holt_best_streak') || '0', 10);
    if (streakCountEl) streakCountEl.textContent = currentStreak;
    if (bestStreakEl) bestStreakEl.textContent = bestStreak;
}

// Save streak to localStorage
function saveStreakToStorage() {
    localStorage.setItem('holt_streak', String(currentStreak));
    localStorage.setItem('holt_best_streak', String(bestStreak));
}

// Load episodes grouped by season
async function loadEpisodes() {
    try {
        const response = await fetch('/game/episodes');
        const data = await response.json();
        episodesBySeason = data.episodes_by_season || {};
        
        // Populate season dropdown
        if (guessSeason) {
            guessSeason.innerHTML = '<option value="">Select season...</option>';
            for (let s = 1; s <= 8; s++) {
                if (episodesBySeason[s]) {
                    guessSeason.innerHTML += `<option value="${s}">Season ${s}</option>`;
                }
            }
        }
    } catch (error) {
        console.error('Failed to load episodes:', error);
    }
}

// Update episode dropdown when season changes
function updateEpisodeDropdown(season) {
    if (!guessEpisode) return;
    
    guessEpisode.innerHTML = '<option value="">Select episode...</option>';
    
    if (season && episodesBySeason[season]) {
        episodesBySeason[season].forEach(ep => {
            guessEpisode.innerHTML += `<option value="${ep}">${ep}</option>`;
        });
    }
}

// Load a new quote
async function loadNewQuote() {
    quoteText.textContent = 'Loading quote...';
    guessInput.value = '';
    if (guessSeason) guessSeason.value = '';
    if (guessEpisode) {
        guessEpisode.innerHTML = '<option value="">Select episode...</option>';
        guessEpisode.value = '';
    }
    guessInput.disabled = false;
    submitBtn.disabled = false;
    nextBtn.classList.add('hidden');
    resultDiv.classList.add('hidden');
    currentAnswer = null;
    currentEpisode = null;
    currentSeason = null;

    try {
        // Always hide episode hint - player must guess both
        const response = await fetch('/game/quote?hard_mode=true');
        const data = await response.json();

        if (data.error) {
            quoteText.textContent = data.error;
            return;
        }

        quoteText.textContent = `"${data.text}"`;
        currentAnswer = data.answer_character;
        currentEpisode = data.answer_episode;
        currentSeason = data.answer_season;
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

    // Season change -> update episodes
    if (guessSeason) {
        guessSeason.addEventListener('change', (e) => {
            updateEpisodeDropdown(e.target.value);
        });
    }

    // Autocomplete
    guessInput.addEventListener('input', handleAutocomplete);
    guessInput.addEventListener('focus', handleAutocomplete);
    document.addEventListener('click', (e) => {
        if (!guessInput.contains(e.target) && !autocompleteList.contains(e.target)) {
            autocompleteList.classList.add('hidden');
        }
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
        // Build query params - check character + episode
        let params = `guess=${encodeURIComponent(guess)}&answer=${encodeURIComponent(currentAnswer)}`;
        params += `&answer_episode=${encodeURIComponent(currentEpisode || '')}`;
        
        if (guessEpisode && guessEpisode.value) {
            params += `&guess_episode=${encodeURIComponent(guessEpisode.value)}`;
        }
        
        const response = await fetch(`/game/verify?${params}`, {
            method: 'POST'
        });
        const data = await response.json();

        // Both character AND episode must be correct for streak
        const isCorrect = data.character_correct && data.episode_correct;
        
        if (isCorrect) {
            currentStreak++;
            if (currentStreak > bestStreak) {
                bestStreak = currentStreak;
            }
            resultDiv.className = 'mt-6 p-4 rounded-lg bg-green-50 border border-green-200';
        } else {
            currentStreak = 0;
            resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-50 border border-red-200';
        }

        if (streakCountEl) streakCountEl.textContent = currentStreak;
        if (bestStreakEl) bestStreakEl.textContent = bestStreak;

        saveStreakToStorage();

        // Build result message
        let resultHtml = '';
        if (isCorrect) {
            resultHtml = `<p class="text-green-800 font-semibold">Correct! ${currentAnswer} - ${currentEpisode}</p>`;
        } else {
            resultHtml = `<p class="text-red-800 font-semibold">`;
            if (data.character_correct) {
                resultHtml += `Character: ✓ Correct<br>`;
            } else {
                resultHtml += `Character: ✗ ${currentAnswer}<br>`;
            }
            if (data.episode_correct) {
                resultHtml += `Episode: ✓ Correct`;
            } else {
                resultHtml += `Episode: ✗ ${currentEpisode} (Season ${currentSeason})`;
            }
            resultHtml += `</p>`;
        }
        
        resultDiv.innerHTML = resultHtml;
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

