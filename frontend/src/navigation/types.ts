export type RootStackParamList = {
  Login: undefined;
  Loading: undefined;
  GuestFlight: undefined;
  Home: {
    userData?: {
      ticketNumber: string;
      flightNumber: string;
    } | null;
  };
};

export type HomeTabParamList = {
  Arrivals: undefined;
  Departures: undefined;
  Map: undefined;
  Shops: undefined;
  Parking: undefined;
  About: undefined;
};