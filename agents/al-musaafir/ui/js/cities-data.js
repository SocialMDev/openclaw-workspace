// Al-Musaafir Cities Data - Centralized city database with 95+ cities
// Organized by region for grouped dropdown display

const CITIES = {
    // === SAUDI ARABIA (15 cities) ===
    'RUH': { name: 'Riyadh', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'JED': { name: 'Jeddah', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'DMM': { name: 'Dammam', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'MED': { name: 'Medina', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'AHB': { name: 'Abha', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'GIZ': { name: 'Jazan', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'TUU': { name: 'Tabuk', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'TIF': { name: 'Taif', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'ELQ': { name: 'Qassim', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'HOF': { name: 'Al-Hofuf', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'HAS': { name: 'Hail', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'AJF': { name: 'Al-Jouf', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'EAM': { name: 'Najran', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'YNB': { name: 'Yanbu', region: 'Saudi Arabia', country: 'Saudi Arabia' },
    'ABT': { name: 'Al-Baha', region: 'Saudi Arabia', country: 'Saudi Arabia' },

    // === MIDDLE EAST (9 cities) ===
    'DXB': { name: 'Dubai', region: 'Middle East', country: 'UAE' },
    'AUH': { name: 'Abu Dhabi', region: 'Middle East', country: 'UAE' },
    'DOH': { name: 'Doha', region: 'Middle East', country: 'Qatar' },
    'BAH': { name: 'Bahrain', region: 'Middle East', country: 'Bahrain' },
    'KWI': { name: 'Kuwait City', region: 'Middle East', country: 'Kuwait' },
    'MCT': { name: 'Muscat', region: 'Middle East', country: 'Oman' },
    'AMM': { name: 'Amman', region: 'Middle East', country: 'Jordan' },
    'BEY': { name: 'Beirut', region: 'Middle East', country: 'Lebanon' },
    'TLV': { name: 'Tel Aviv', region: 'Middle East', country: 'Israel' },

    // === EUROPE (24 cities) ===
    'LON': { name: 'London', region: 'Europe', country: 'UK' },
    'PAR': { name: 'Paris', region: 'Europe', country: 'France' },
    'BER': { name: 'Berlin', region: 'Europe', country: 'Germany' },
    'FRA': { name: 'Frankfurt', region: 'Europe', country: 'Germany' },
    'MUC': { name: 'Munich', region: 'Europe', country: 'Germany' },
    'AMS': { name: 'Amsterdam', region: 'Europe', country: 'Netherlands' },
    'MAD': { name: 'Madrid', region: 'Europe', country: 'Spain' },
    'BCN': { name: 'Barcelona', region: 'Europe', country: 'Spain' },
    'ROM': { name: 'Rome', region: 'Europe', country: 'Italy' },
    'MIL': { name: 'Milan', region: 'Europe', country: 'Italy' },
    'VIE': { name: 'Vienna', region: 'Europe', country: 'Austria' },
    'ZRH': { name: 'Zurich', region: 'Europe', country: 'Switzerland' },
    'CPH': { name: 'Copenhagen', region: 'Europe', country: 'Denmark' },
    'OSL': { name: 'Oslo', region: 'Europe', country: 'Norway' },
    'STO': { name: 'Stockholm', region: 'Europe', country: 'Sweden' },
    'HEL': { name: 'Helsinki', region: 'Europe', country: 'Finland' },
    'WAW': { name: 'Warsaw', region: 'Europe', country: 'Poland' },
    'PRG': { name: 'Prague', region: 'Europe', country: 'Czech Republic' },
    'BUD': { name: 'Budapest', region: 'Europe', country: 'Hungary' },
    'ATH': { name: 'Athens', region: 'Europe', country: 'Greece' },
    'IST': { name: 'Istanbul', region: 'Europe', country: 'Turkey' },
    'LIS': { name: 'Lisbon', region: 'Europe', country: 'Portugal' },
    'DUB': { name: 'Dublin', region: 'Europe', country: 'Ireland' },
    'MAN': { name: 'Manchester', region: 'Europe', country: 'UK' },

    // === ASIA (15 cities) ===
    'TYO': { name: 'Tokyo', region: 'Asia', country: 'Japan' },
    'OSA': { name: 'Osaka', region: 'Asia', country: 'Japan' },
    'ICN': { name: 'Seoul', region: 'Asia', country: 'South Korea' },
    'PEK': { name: 'Beijing', region: 'Asia', country: 'China' },
    'PVG': { name: 'Shanghai', region: 'Asia', country: 'China' },
    'HKG': { name: 'Hong Kong', region: 'Asia', country: 'China' },
    'CAN': { name: 'Guangzhou', region: 'Asia', country: 'China' },
    'SIN': { name: 'Singapore', region: 'Asia', country: 'Singapore' },
    'BKK': { name: 'Bangkok', region: 'Asia', country: 'Thailand' },
    'KUL': { name: 'Kuala Lumpur', region: 'Asia', country: 'Malaysia' },
    'CGK': { name: 'Jakarta', region: 'Asia', country: 'Indonesia' },
    'MNL': { name: 'Manila', region: 'Asia', country: 'Philippines' },
    'DEL': { name: 'Delhi', region: 'Asia', country: 'India' },
    'BOM': { name: 'Mumbai', region: 'Asia', country: 'India' },
    'BLR': { name: 'Bangalore', region: 'Asia', country: 'India' },

    // === NORTH AMERICA (15 cities) ===
    'NYC': { name: 'New York', region: 'North America', country: 'USA' },
    'LAX': { name: 'Los Angeles', region: 'North America', country: 'USA' },
    'ORD': { name: 'Chicago', region: 'North America', country: 'USA' },
    'SFO': { name: 'San Francisco', region: 'North America', country: 'USA' },
    'MIA': { name: 'Miami', region: 'North America', country: 'USA' },
    'DFW': { name: 'Dallas', region: 'North America', country: 'USA' },
    'SEA': { name: 'Seattle', region: 'North America', country: 'USA' },
    'BOS': { name: 'Boston', region: 'North America', country: 'USA' },
    'ATL': { name: 'Atlanta', region: 'North America', country: 'USA' },
    'DEN': { name: 'Denver', region: 'North America', country: 'USA' },
    'IAH': { name: 'Houston', region: 'North America', country: 'USA' },
    'WAS': { name: 'Washington DC', region: 'North America', country: 'USA' },
    'YYZ': { name: 'Toronto', region: 'North America', country: 'Canada' },
    'YVR': { name: 'Vancouver', region: 'North America', country: 'Canada' },
    'MEX': { name: 'Mexico City', region: 'North America', country: 'Mexico' },

    // === SOUTH AMERICA (6 cities) ===
    'GRU': { name: 'Sao Paulo', region: 'South America', country: 'Brazil' },
    'EZE': { name: 'Buenos Aires', region: 'South America', country: 'Argentina' },
    'BOG': { name: 'Bogota', region: 'South America', country: 'Colombia' },
    'SCL': { name: 'Santiago', region: 'South America', country: 'Chile' },
    'LIM': { name: 'Lima', region: 'South America', country: 'Peru' },
    'GIG': { name: 'Rio de Janeiro', region: 'South America', country: 'Brazil' },

    // === AFRICA (7 cities) ===
    'CAI': { name: 'Cairo', region: 'Africa', country: 'Egypt' },
    'JNB': { name: 'Johannesburg', region: 'Africa', country: 'South Africa' },
    'CPT': { name: 'Cape Town', region: 'Africa', country: 'South Africa' },
    'NBO': { name: 'Nairobi', region: 'Africa', country: 'Kenya' },
    'ADD': { name: 'Addis Ababa', region: 'Africa', country: 'Ethiopia' },
    'CMN': { name: 'Casablanca', region: 'Africa', country: 'Morocco' },
    'LOS': { name: 'Lagos', region: 'Africa', country: 'Nigeria' },

    // === OCEANIA (4 cities) ===
    'SYD': { name: 'Sydney', region: 'Oceania', country: 'Australia' },
    'MEL': { name: 'Melbourne', region: 'Oceania', country: 'Australia' },
    'BNE': { name: 'Brisbane', region: 'Oceania', country: 'Australia' },
    'AKL': { name: 'Auckland', region: 'Oceania', country: 'New Zealand' }
};

// Region display order (Saudi Arabia first)
const REGION_ORDER = [
    'Saudi Arabia',
    'Middle East',
    'Europe',
    'Asia',
    'North America',
    'South America',
    'Africa',
    'Oceania'
];
