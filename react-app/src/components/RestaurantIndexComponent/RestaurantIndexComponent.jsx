import React from "react";
import { useState, useEffect } from "react";
import api from "../../utilities/user-services";
import { Link } from "react-router-dom";
import useApi from "../../hooks/useApi";

export default function RestaurantIndexComponent({ selectedDay }) {
  // const [restaurants, setRestaurants] = useState([]);
  // const [isLoading, setIsLoading] = useState(false);
  // Assume passing the restaruaunt id as a state
  const { data: restaurants, loading, error, request } = useApi();

  // Fetches restaurants by day
  // Strigify the selectedDay to be used in the API call in DateSelector
  // const selectedDayString = encodeURIComponent(selectedDay);
  // After pass as the uri component encodeURIComponent(selectedDay)

  useEffect(() => {
    const fetchRestaurantByDay = async () => {
      if (selectedDay) {
        // setRestaurants([]);
        // return;
        request(api.get, `/restaurants/day/${encodeURIComponent(selectedDay)}`);
        console.log(`restaurants: ${restaurants}`);
      }
    };
    fetchRestaurantByDay();
  }, [selectedDay, request]);


  if (!selectedDay) {
    return <div>Please select a day to see available restaurants</div>;
  } else if (loading) {
    return <div>Loading...</div>;
  } else if (error) {
    return <div>Error: {error.message}</div>;
  } else {
    return (
      <div>
        <h2>Restaurants</h2>
        {restaurants?.length > 0 ? (
          <ul>
            {restaurants.map((restaurant) => (
              <li key={restaurant.id}>
                <Link to={`/restaurants/${restaurant.id}`}>
                  {restaurant.name}
                </Link>
                <img
                  src={restaurant.image}
                  alt={restaurant.name}
                  className="w-24"
                />
                <p>{restaurant.description}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No restaurants available for the selected day</p>
        )}
      </div>
    );
  }
}
