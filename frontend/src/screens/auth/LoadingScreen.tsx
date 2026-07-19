import React, { useEffect, useState } from 'react';
import { Animated, Easing, Image, StyleSheet, Text, View } from 'react-native';

export default function LoadingScreen() {
  const [progress] = useState(new Animated.Value(0));
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    Animated.timing(progress, {
      toValue: 1,
      duration: 2000,
      easing: Easing.linear,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  const width = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      {/* Logo Section */}
      {imageError ? (
        <Text style={styles.logoText}>LOGO</Text>
      ) : (
        <Image
          source={require('../../../assets/logo.png')} 
          style={styles.logo}
          resizeMode="contain"
          onError={() => setImageError(true)}
        />
      )}

      <Text style={styles.text}>Loading...</Text>

      <View style={styles.progressContainer}>
        <Animated.View style={[styles.progressBar, { width }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0C2340',
  },
  logo: {
    width: 200,
    height: 200,
    marginBottom: 30,
  },
  logoText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 22,
    marginBottom: 30,
  },
  text: {
    color: '#fff',
    fontSize: 22,
    marginBottom: 30,
  },
  progressContainer: {
    width: '80%',
    height: 8,
    backgroundColor: '#1E3A8A',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#FFD100',
  },
});
