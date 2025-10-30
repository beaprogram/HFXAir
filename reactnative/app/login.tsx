import React, { useState } from 'react'; 
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, StatusBar } from 'react-native';

interface LoginScreenProps {
  onLogin: (ticketNumber: string, flightNumber: string) => void;
}

export default function LoginScreen({ onLogin }: LoginScreenProps) {
  const [ticketNumber, setTicketNumber] = useState('');
  const [flightNumber, setFlightNumber] = useState('');
  const [imageError, setImageError] = useState(false);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0C2340" />

      {/* Logo */}
      <View style={styles.logoWrapper}>
        {imageError ? (
          <View style={styles.logoFallback}>
            <Text style={styles.logoText}>LOGO</Text>
          </View>
        ) : (
          <Image
            source={require('../assets/application_logo.png')} 
            style={styles.logo}
            resizeMode="cover"
            onError={() => setImageError(true)}
          />
        )}
      </View>

      <Text style={styles.title}>Welcome Aboard</Text>
      <Text style={styles.subtitle}>Sign in to manage your flight</Text>

      {/* Inputs */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Ticket Number"
          placeholderTextColor="#ccc"
          value={ticketNumber}
          onChangeText={setTicketNumber}
        />
        <TextInput
          style={styles.input}
          placeholder="Flight Number"
          placeholderTextColor="#ccc"
          value={flightNumber}
          onChangeText={setFlightNumber}
          autoCapitalize="characters"
        />
      </View>

      <TouchableOpacity
        style={styles.button}
        onPress={() => onLogin(ticketNumber, flightNumber)}
      >
        <Text style={styles.buttonText}>Log In</Text>
      </TouchableOpacity >

      <TouchableOpacity
        style={styles.guestButton}
        onPress={() => onLogin('', '')}
      >
        <Text style={styles.guestButtonText}>Continue as Guest</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>© 2025 Airline App</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0C2340', paddingHorizontal: 30 },
  logoWrapper: { width: 150, height: 150, borderRadius: 75, overflow: 'hidden', borderWidth: 3, borderColor: '#fff', marginBottom: 30, backgroundColor: '#fff', justifyContent: 'center', alignItems: 'center' },
  logo: { width: '100%', height: '100%' },
  logoFallback: { justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', width: '100%', height: '100%' },
  logoText: { color: '#0C2340', fontWeight: 'bold', fontSize: 22 },
  title: { fontSize: 28, fontWeight: '700', color: '#fff', marginBottom: 6, textAlign: 'center' },
  subtitle: { fontSize: 16, color: '#b0b0b0', marginBottom: 40, textAlign: 'center' },
  inputContainer: { width: '100%', marginBottom: 25 },
  input: { height: 52, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 10, paddingHorizontal: 16, color: '#fff', marginBottom: 14, borderWidth: 1, borderColor: 'rgba(255,255,255,0.25)' },
  button: { backgroundColor: '#fff', paddingVertical: 14, borderRadius: 10, width: '100%', alignItems: 'center' },
  buttonText: { color: '#0C2340', fontSize: 18, fontWeight: '700' },
  guestButton: { backgroundColor: 'transparent', paddingVertical: 14, borderRadius: 10, width: '100%', alignItems: 'center', borderWidth: 2, borderColor: '#fff', marginTop: 12 },
  guestButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  footer: { color: '#999', fontSize: 12, marginTop: 40 },
});
//testing