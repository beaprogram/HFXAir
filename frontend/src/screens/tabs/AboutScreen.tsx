import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Linking } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';

interface AboutScreenProps {
  showHeader?: boolean;
}

const contactInfo = [
  { icon: 'phone', label: 'General Inquiries', value: '1-877-359-4797', type: 'phone' },
  { icon: 'envelope', label: 'Email', value: 'info@hiaa.ca', type: 'email' },
  { icon: 'globe', label: 'Website', value: 'www.halifaxstanfield.ca', type: 'url' },
  { icon: 'map-marker', label: 'Address', value: '1 Bell Blvd, Enfield, NS B2T 1K2', type: 'address' },
];

const services = [
  {
    title: 'WiFi',
    description: 'Free high-speed WiFi throughout the terminal',
    icon: 'wifi',
  },
  {
    title: 'Lounges',
    description: 'Premium lounges available for eligible passengers',
    icon: 'star',
  },
  {
    title: 'Accessibility',
    description: 'Full accessibility services and assistance available',
    icon: 'wheelchair',
  },
  {
    title: 'Pet Relief',
    description: 'Pet relief areas located near gate areas',
    icon: 'paw',
  },
  {
    title: 'Charging Stations',
    description: 'Power outlets and USB charging throughout terminal',
    icon: 'bolt',
  },
  {
    title: 'Baggage Storage',
    description: 'Short-term baggage storage services available',
    icon: 'archive',
  },
];

const emergencyContacts = [
  { label: 'Airport Security', number: '902-873-4422' },
  { label: 'Medical Emergency', number: '911' },
  { label: 'Lost & Found', number: '902-873-4422' },
  { label: 'Customer Service', number: '1-877-359-4797' },
];

export default function AboutScreen(_props: AboutScreenProps) {
  const handleContact = (type: string, value: string) => {
    switch (type) {
      case 'phone':
        Linking.openURL(`tel:${value.replace(/[^0-9]/g, '')}`);
        break;
      case 'email':
        Linking.openURL(`mailto:${value}`);
        break;
      case 'url':
        Linking.openURL(`https://${value}`);
        break;
      default:
        break;
    }
  };

  return (
    <View style={styles.container}>
      {/* Content */}
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.content}>
          {/* Airport Info */}
          <View style={styles.section}>
            <Text style={styles.airportName}>Halifax Stanfield</Text>
            <Text style={styles.airportSubtitle}>International Airport (YHZ)</Text>
            <Text style={styles.description}>
              Atlantic Canada's primary airport serving Halifax and the Maritime provinces. 
              Connecting you to destinations across Canada and around the world.
            </Text>
          </View>

          {/* Contact Information */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Contact Information</Text>
            {contactInfo.map((contact, index) => (
              <TouchableOpacity
                key={index}
                style={styles.contactItem}
                onPress={() => handleContact(contact.type, contact.value)}
              >
                <View style={styles.contactIcon}>
                  <Icon name={contact.icon} size={18} color="#0C2340" />
                </View>
                <View style={styles.contactInfo}>
                  <Text style={styles.contactLabel}>{contact.label}</Text>
                  <Text style={styles.contactValue}>{contact.value}</Text>
                </View>
                {contact.type !== 'address' && (
                  <Icon name="chevron-right" size={14} color="#999" />
                )}
              </TouchableOpacity>
            ))}
          </View>

          {/* Services & Amenities */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Services & Amenities</Text>
            <View style={styles.servicesGrid}>
              {services.map((service, index) => (
                <View key={index} style={styles.serviceCard}>
                  <View style={styles.serviceIcon}>
                    <Icon name={service.icon} size={24} color="#0C2340" />
                  </View>
                  <Text style={styles.serviceTitle}>{service.title}</Text>
                  <Text style={styles.serviceDescription}>{service.description}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Emergency Contacts */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Emergency Contacts</Text>
            <View style={styles.emergencyCard}>
              {emergencyContacts.map((contact, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.emergencyItem}
                  onPress={() => Linking.openURL(`tel:${contact.number.replace(/[^0-9]/g, '')}`)}
                >
                  <View style={styles.emergencyInfo}>
                    <Icon name="phone" size={16} color="#FF6B6B" />
                    <Text style={styles.emergencyLabel}>{contact.label}</Text>
                  </View>
                  <Text style={styles.emergencyNumber}>{contact.number}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Operating Hours */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Operating Hours</Text>
            <View style={styles.hoursCard}>
              <View style={styles.hoursItem}>
                <Icon name="clock-o" size={18} color="#0C2340" />
                <Text style={styles.hoursText}>Terminal: Open 24/7</Text>
              </View>
              <View style={styles.hoursItem}>
                <Icon name="building" size={18} color="#0C2340" />
                <Text style={styles.hoursText}>Check-in: Opens 3 hours before first flight</Text>
              </View>
              <View style={styles.hoursItem}>
                <Icon name="shield" size={18} color="#0C2340" />
                <Text style={styles.hoursText}>Security: Available during operating hours</Text>
              </View>
            </View>
          </View>

          {/* FAQ */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Frequently Asked Questions</Text>
            <View style={styles.faqCard}>
              <Text style={styles.faqQuestion}>How early should I arrive?</Text>
              <Text style={styles.faqAnswer}>
                2 hours for domestic flights, 3 hours for international flights.
              </Text>
            </View>
            <View style={styles.faqCard}>
              <Text style={styles.faqQuestion}>Is WiFi free?</Text>
              <Text style={styles.faqAnswer}>
                Yes, free high-speed WiFi is available throughout the terminal.
              </Text>
            </View>
            <View style={styles.faqCard}>
              <Text style={styles.faqQuestion}>Where can I charge my devices?</Text>
              <Text style={styles.faqAnswer}>
                Charging stations are available in all gate areas and lounges.
              </Text>
            </View>
          </View>

          {/* App Info */}
          <View style={styles.appInfo}>
            <Text style={styles.appVersion}>Halifax Stanfield Airport App</Text>
            <Text style={styles.appVersionNumber}>Version 1.0.0</Text>
            <Text style={styles.copyright}>© 2025 Halifax International Airport Authority</Text>
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
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  airportName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0C2340',
    textAlign: 'center',
  },
  airportSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 4,
    marginBottom: 12,
  },
  description: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 12,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  contactIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFD100',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contactInfo: {
    flex: 1,
  },
  contactLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
  },
  contactValue: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
  servicesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 12,
  },
  serviceCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  serviceIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  serviceTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 4,
    textAlign: 'center',
  },
  serviceDescription: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
    lineHeight: 16,
  },
  emergencyCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 8,
  },
  emergencyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  emergencyInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  emergencyLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  emergencyNumber: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '600',
  },
  hoursCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  hoursItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  hoursText: {
    fontSize: 14,
    color: '#666',
  },
  faqCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
  },
  faqQuestion: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0C2340',
    marginBottom: 6,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  appInfo: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  appVersion: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0C2340',
  },
  appVersionNumber: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  copyright: {
    fontSize: 11,
    color: '#999',
    marginTop: 8,
  },
});
