import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';

interface ParkingScreenProps {
  showHeader?: boolean;
}

const parkingOptions = [
  {
    id: '1',
    name: 'Short-Term Parking',
    rate: '$4.00 per 30 minutes',
    dailyMax: '$24.00',
    features: ['Closest to terminal', 'Covered parking', 'Perfect for pickups/dropoffs'],
    availability: 'High',
  },
  {
    id: '2',
    name: 'Long-Term Parking',
    rate: '$18.00 per day',
    dailyMax: '$18.00',
    features: ['Shuttle service to terminal', 'Outdoor parking', 'Best for extended trips'],
    availability: 'Medium',
  },
  {
    id: '3',
    name: 'Economy Parking',
    rate: '$14.00 per day',
    dailyMax: '$14.00',
    features: ['Most affordable', 'Shuttle service', 'Outdoor parking'],
    availability: 'High',
  },
  {
    id: '4',
    name: 'Valet Parking',
    rate: '$28.00 per day',
    dailyMax: '$28.00',
    features: ['Premium service', 'Door-to-door', 'Indoor parking', 'Car wash available'],
    availability: 'Low',
  },
];

export default function ParkingScreen(_props: ParkingScreenProps) {
  const [days, setDays] = useState('');
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const calculateCost = (rate: string, dailyMax: string) => {
    const numDays = parseInt(days, 10) || 0;
    if (numDays <= 0) return null;
    
    const pricePerDay = parseFloat(dailyMax.replace('$', ''));
    return (pricePerDay * numDays).toFixed(2);
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case 'High':
        return '#4CAF50';
      case 'Medium':
        return '#FFA726';
      case 'Low':
        return '#FF6B6B';
      default:
        return '#999';
    }
  };

  return (
    <View style={styles.container}>
      {/* Calculator */}
      <View style={styles.calculatorSection}>
        <Text style={styles.calculatorTitle}>Parking Cost Calculator</Text>
        <View style={styles.inputRow}>
          <Text style={styles.inputLabel}>Number of days:</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter days"
            placeholderTextColor="#999"
            keyboardType="numeric"
            value={days}
            onChangeText={setDays}
          />
        </View>
      </View>

      {/* Content */}
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>Parking Options</Text>
          
          {parkingOptions.map((option) => {
            const cost = calculateCost(option.rate, option.dailyMax);
            return (
              <TouchableOpacity
                key={option.id}
                style={[
                  styles.parkingCard,
                  selectedOption === option.id && styles.parkingCardSelected
                ]}
                onPress={() => setSelectedOption(option.id)}
              >
                <View style={styles.cardHeader}>
                  <Text style={styles.optionName}>{option.name}</Text>
                  <View style={[
                    styles.availabilityBadge,
                    { backgroundColor: getAvailabilityColor(option.availability) }
                  ]}>
                    <Text style={styles.availabilityText}>{option.availability}</Text>
                  </View>
                </View>

                <View style={styles.rateSection}>
                  <Text style={styles.rateText}>{option.rate}</Text>
                  <Text style={styles.dailyMaxText}>Daily Max: {option.dailyMax}</Text>
                </View>

                {cost && (
                  <View style={styles.costEstimate}>
                    <Icon name="calculator" size={16} color="#0C2340" />
                    <Text style={styles.costText}>
                      Estimated cost for {days} day{parseInt(days, 10) !== 1 ? 's' : ''}: ${cost}
                    </Text>
                  </View>
                )}

                <View style={styles.featuresSection}>
                  {option.features.map((feature, index) => (
                    <View key={index} style={styles.featureItem}>
                      <Icon name="check-circle" size={14} color="#4CAF50" />
                      <Text style={styles.featureText}>{feature}</Text>
                    </View>
                  ))}
                </View>
              </TouchableOpacity>
            );
          })}

          {/* Additional Info */}
          <View style={styles.infoSection}>
            <Text style={styles.infoTitle}>Payment Methods</Text>
            <View style={styles.infoItem}>
              <Icon name="credit-card" size={16} color="#666" />
              <Text style={styles.infoText}>Credit/Debit Cards</Text>
            </View>
            <View style={styles.infoItem}>
              <Icon name="money" size={16} color="#666" />
              <Text style={styles.infoText}>Cash (at exit)</Text>
            </View>
            <View style={styles.infoItem}>
              <Icon name="mobile-phone" size={16} color="#666" />
              <Text style={styles.infoText}>Mobile Payment Apps</Text>
            </View>
          </View>

          <View style={styles.infoSection}>
            <Text style={styles.infoTitle}>Important Information</Text>
            <Text style={styles.infoText}>• Lost ticket fee: $50.00</Text>
            <Text style={styles.infoText}>• Oversized vehicle rates may apply</Text>
            <Text style={styles.infoText}>• ADA accessible parking available</Text>
            <Text style={styles.infoText}>• 24/7 security monitoring</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  calculatorSection: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  calculatorTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 12,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  inputLabel: {
    fontSize: 14,
    color: '#666',
  },
  input: {
    flex: 1,
    height: 44,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 16,
  },
  parkingCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  parkingCardSelected: {
    borderColor: '#FFD100',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  optionName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0C2340',
  },
  availabilityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  availabilityText: {
    fontSize: 11,
    color: '#fff',
    fontWeight: '600',
  },
  rateSection: {
    marginBottom: 12,
  },
  rateText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  dailyMaxText: {
    fontSize: 13,
    color: '#999',
    marginTop: 2,
  },
  costEstimate: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#E8F5E9',
    padding: 10,
    borderRadius: 8,
    marginBottom: 12,
  },
  costText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
  },
  featuresSection: {
    gap: 8,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  featureText: {
    fontSize: 13,
    color: '#666',
  },
  infoSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 12,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
});
