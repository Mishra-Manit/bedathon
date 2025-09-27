import { useState, useEffect } from 'react';
import { ApartmentService, ApartmentComplex, ApartmentFilters } from './apartmentService';

export function useApartments(filters: ApartmentFilters = {}) {
  const [apartments, setApartments] = useState<ApartmentComplex[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApartments = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await ApartmentService.getApartments(filters);
        setApartments(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch apartments');
        console.error('Error fetching apartments:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchApartments();
  }, [JSON.stringify(filters)]);

  const refetch = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ApartmentService.getApartments(filters);
      setApartments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch apartments');
      console.error('Error fetching apartments:', err);
    } finally {
      setLoading(false);
    }
  };

  return { apartments, loading, error, refetch };
}

export function useApartment(id: string) {
  const [apartment, setApartment] = useState<ApartmentComplex | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApartment = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await ApartmentService.getApartment(id);
        setApartment(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch apartment');
        console.error('Error fetching apartment:', err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchApartment();
    }
  }, [id]);

  return { apartment, loading, error };
}
