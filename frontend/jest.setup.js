require('react-native-gesture-handler/jestSetup');

jest.mock('@react-native-firebase/app', () => ({}));
jest.mock('@react-native-firebase/messaging', () => {
  const messaging = () => ({
    getToken: jest.fn().mockResolvedValue('test-device-token'),
  });
  return messaging;
});

jest.mock('react-native-vector-icons/FontAwesome', () => 'FontAwesomeIcon');
