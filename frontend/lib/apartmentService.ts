// Frontend service for apartment data
export interface ApartmentComplex {
  id: string;
  name: string;
  phone_number?: string;
  notes?: string;
  lease_term?: number;
  lease_type?: string;
  studio_cost?: string;
  one_bedroom_cost?: string;
  two_bedroom_cost?: string;
  three_bedroom_cost?: string;
  four_bedroom_cost?: string;
  five_bedroom_cost?: string;
  application_fee?: number;
  security_deposit?: string;
  pets_allowed?: boolean;
  parking_included?: boolean;
  furniture_included?: boolean;
  utilities_included?: string;
  laundry?: string;
  additional_fees?: string;
  distance_to_burruss?: number;
  bus_stop_nearby?: boolean;
  address?: string;
  created_at: string;
  updated_at: string;
}

export interface ApartmentFilters {
  search?: string;
  min_bedrooms?: number;
  max_bedrooms?: number;
  max_distance?: number;
  pets_allowed?: boolean;
  parking_included?: boolean;
  furniture_included?: boolean;
  limit?: number;
  offset?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApartmentService {
  static async getApartments(filters: ApartmentFilters = {}): Promise<ApartmentComplex[]> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await fetch(`${API_BASE_URL}/apartments?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch apartments: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async getApartment(id: string): Promise<ApartmentComplex> {
    const response = await fetch(`${API_BASE_URL}/apartments/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch apartment: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async importApartmentData(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/apartments/import`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to import apartment data: ${response.statusText}`);
    }
  }
}

// Helper function to format apartment data for display
export function formatApartmentForDisplay(apartment: ApartmentComplex) {
  const getPriceRange = () => {
    const prices = [
      apartment.studio_cost,
      apartment.one_bedroom_cost,
      apartment.two_bedroom_cost,
      apartment.three_bedroom_cost,
      apartment.four_bedroom_cost,
      apartment.five_bedroom_cost
    ].filter(price => price && price !== 'X');

    if (prices.length === 0) return 'Contact for pricing';
    
    // Parse price ranges and find min/max
    const numericPrices: number[] = [];
    prices.forEach(price => {
      if (price?.includes('-')) {
        const [min, max] = price.split('-').map(p => parseInt(p.trim()));
        if (!isNaN(min)) numericPrices.push(min);
        if (!isNaN(max)) numericPrices.push(max);
      } else {
        const num = parseInt(price?.replace(/[^\d]/g, '') || '0');
        if (num > 0) numericPrices.push(num);
      }
    });

    if (numericPrices.length === 0) return 'Contact for pricing';
    
    const minPrice = Math.min(...numericPrices);
    const maxPrice = Math.max(...numericPrices);
    
    if (minPrice === maxPrice) {
      return `$${minPrice}/month`;
    } else {
      return `$${minPrice}-$${maxPrice}/month`;
    }
  };

  const getBedroomCount = () => {
    const counts = [];
    if (apartment.studio_cost && apartment.studio_cost !== 'X') counts.push('Studio');
    if (apartment.one_bedroom_cost && apartment.one_bedroom_cost !== 'X') counts.push('1BR');
    if (apartment.two_bedroom_cost && apartment.two_bedroom_cost !== 'X') counts.push('2BR');
    if (apartment.three_bedroom_cost && apartment.three_bedroom_cost !== 'X') counts.push('3BR');
    if (apartment.four_bedroom_cost && apartment.four_bedroom_cost !== 'X') counts.push('4BR');
    if (apartment.five_bedroom_cost && apartment.five_bedroom_cost !== 'X') counts.push('5BR');
    
    return counts.length > 0 ? counts.join(', ') : 'Various';
  };

  const getUtilities = () => {
    if (!apartment.utilities_included) return 'Contact for details';
    
    try {
      const utilities = JSON.parse(apartment.utilities_included);
      return utilities.length > 0 ? utilities.join(', ') : 'Contact for details';
    } catch {
      return apartment.utilities_included;
    }
  };

  return {
    id: apartment.id,
    name: apartment.name,
    address: apartment.address || 'Address not provided',
    price: getPriceRange(),
    bedrooms: getBedroomCount(),
    distance: apartment.distance_to_burruss 
      ? `${apartment.distance_to_burruss} miles to campus`
      : 'Distance not provided',
    phone: apartment.phone_number || 'Contact not provided',
    utilities: getUtilities(),
    pets: apartment.pets_allowed ? 'Pets allowed' : 'No pets',
    parking: apartment.parking_included ? 'Parking included' : 'Parking not included',
    furniture: apartment.furniture_included ? 'Furnished' : 'Unfurnished',
    laundry: apartment.laundry || 'Contact for details',
    busStop: apartment.bus_stop_nearby ? 'Bus stop nearby' : 'No bus stop',
    notes: apartment.notes || '',
    applicationFee: apartment.application_fee ? `$${apartment.application_fee}` : 'Contact for details',
    securityDeposit: apartment.security_deposit || 'Contact for details',
    additionalFees: apartment.additional_fees || 'None',
    leaseType: apartment.lease_type || 'Contact for details',
    leaseTerm: apartment.lease_term ? `${apartment.lease_term} months` : 'Contact for details'
  };
}
