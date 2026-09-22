export interface BedAvailability {
  icu: number;
  general: number;
  single_private: number;
  deluxe: number;
  status: string;
}

export interface RoomTariffs {
  general: number;
  twin_sharing: number;
  single_private: number;
  deluxe_suite: number;
}

export interface Hospital {
  id: string;
  name: string;
  tagline: string;
  city: string;
  locality: string;
  distance_km: number;
  rating: number;
  reviews_count: number;
  emergency_contact: string;
  emergency_24x7: boolean;
  specialties: string[];
  empanelled_tpas: string[];
  network_status: 'CASHLESS_NETWORK' | 'REIMBURSEMENT_ONLY' | 'NON_NETWORK';
  bed_availability: BedAvailability;
  room_tariffs: RoomTariffs;
  estimated_ambulance_eta_mins: number;
}
