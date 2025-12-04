import { PointOfInterest } from '../types/MapTypes';

export const airportPOIs: PointOfInterest[] = [
  // Gates A
  { id: 'gate-a1', name: 'Gate A1', type: 'gate', latitude: 44.88180, longitude: -63.50720, description: 'Domestic - Air Canada regional flights' },
  { id: 'gate-a2', name: 'Gate A2', type: 'gate', latitude: 44.88175, longitude: -63.50690, description: 'Domestic - WestJet to Toronto' },
  { id: 'gate-a3', name: 'Gate A3', type: 'gate', latitude: 44.88170, longitude: -63.50660, description: 'Domestic - Porter Airlines' },
  { id: 'gate-a4', name: 'Gate A4', type: 'gate', latitude: 44.88165, longitude: -63.50630, description: 'Domestic - Air Canada to Montreal' },
  // Gates B
  { id: 'gate-b1', name: 'Gate B1', type: 'gate', latitude: 44.88145, longitude: -63.50750, description: 'Domestic - Flair Airlines' },
  { id: 'gate-b2', name: 'Gate B2', type: 'gate', latitude: 44.88140, longitude: -63.50720, description: 'Domestic - Swoop flights' },
  { id: 'gate-b3', name: 'Gate B3', type: 'gate', latitude: 44.88135, longitude: -63.50690, description: 'Domestic - WestJet to Calgary' },
  // Gates C (International)
  { id: 'gate-c1', name: 'Gate C1', type: 'gate', latitude: 44.88100, longitude: -63.50850, description: 'International - US flights' },
  { id: 'gate-c2', name: 'Gate C2', type: 'gate', latitude: 44.88095, longitude: -63.50880, description: 'International - Transatlantic' },
  { id: 'gate-c3', name: 'Gate C3', type: 'gate', latitude: 44.88090, longitude: -63.50910, description: 'International - Caribbean' },
  // Restaurants
  { id: 'rest-1', name: 'Tim Hortons', type: 'restaurant', latitude: 44.88050, longitude: -63.50780, description: 'Coffee, donuts, breakfast sandwiches' },
  { id: 'rest-2', name: 'Starbucks', type: 'restaurant', latitude: 44.88110, longitude: -63.50800, description: 'Premium coffee and pastries' },
  { id: 'rest-3', name: 'Subway', type: 'restaurant', latitude: 44.88070, longitude: -63.50820, description: 'Fresh sandwiches made to order' },
  { id: 'rest-4', name: 'The Hungry Traveller', type: 'restaurant', latitude: 44.88120, longitude: -63.50750, description: 'Full-service restaurant & bar' },
  { id: 'rest-5', name: 'Swiss Chalet', type: 'restaurant', latitude: 44.88085, longitude: -63.50770, description: 'Rotisserie chicken and ribs' },
  // Shops
  { id: 'shop-1', name: 'Duty Free Shop', type: 'shop', latitude: 44.88095, longitude: -63.50800, description: 'Tax-free perfumes, alcohol, chocolates' },
  { id: 'shop-2', name: 'Hudson News', type: 'shop', latitude: 44.88060, longitude: -63.50760, description: 'Books, magazines, snacks, travel items' },
  { id: 'shop-3', name: 'Tech on the Go', type: 'shop', latitude: 44.88130, longitude: -63.50700, description: 'Electronics, chargers, headphones' },
  { id: 'shop-4', name: 'Maritime Gifts', type: 'shop', latitude: 44.88075, longitude: -63.50790, description: 'Nova Scotia souvenirs and crafts' },
  // Restrooms
  { id: 'wc-1', name: 'Restroom - Pre-Security', type: 'restroom', latitude: 44.88040, longitude: -63.50800, description: 'Near main entrance, accessible' },
  { id: 'wc-2', name: 'Restroom - Gate A', type: 'restroom', latitude: 44.88160, longitude: -63.50680, description: 'Family restroom available' },
  { id: 'wc-3', name: 'Restroom - Gate B', type: 'restroom', latitude: 44.88140, longitude: -63.50740, description: 'Accessible facilities' },
  { id: 'wc-4', name: 'Restroom - International', type: 'restroom', latitude: 44.88090, longitude: -63.50870, description: 'Showers available' },
  // Charging
  { id: 'charge-1', name: 'Charging - Gate A', type: 'charging', latitude: 44.88170, longitude: -63.50670, description: 'Free USB and power outlets' },
  { id: 'charge-2', name: 'Charging - Gate B', type: 'charging', latitude: 44.88138, longitude: -63.50710, description: 'Multiple charging points' },
  { id: 'charge-3', name: 'Charging Lounge', type: 'charging', latitude: 44.88080, longitude: -63.50760, description: 'Work desks with power' },
  // Info & Security
  { id: 'info-1', name: 'Information Desk', type: 'info', latitude: 44.88030, longitude: -63.50830, description: 'Airport help and lost & found' },
  { id: 'security-1', name: 'Security - Main', type: 'security', latitude: 44.88055, longitude: -63.50810, description: 'CATSA screening checkpoint' },
  { id: 'security-2', name: 'Security - US Preclearance', type: 'security', latitude: 44.88085, longitude: -63.50860, description: 'US Customs & Border' },
];
