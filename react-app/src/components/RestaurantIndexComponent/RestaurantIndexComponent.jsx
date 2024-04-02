import React from "react";
import { useState, useEffect } from "react";
import api from "../../utilities/user-services";
import { Link } from "react-router-dom";
import useApi from "../../hooks/useApi";

export default function RestaurantIndexComponent({ selectedDay }) {
  const [restaurants, setRestaurants] = useState([]);
  const { data: apiRestaurants, loading, error, request } = useApi();

  // Fetches restaurants by day
  // Strigify the selectedDay to be used in the API call in DateSelector
  // const selectedDayString = encodeURIComponent(selectedDay);
  // After pass as the uri component encodeURIComponent(selectedDay)
  // If restaurants is empty, set it to an empty array

  // useEffect(() => {
  //   const fetchRestaurantByDay = async () => {
  //     if (selectedDay) {
  //       const restaurants = await request(
  //         api.get,
  //         `/restaurants/day/${encodeURIComponent(selectedDay)}`
  //       );
  //       setRestaurants(restaurants || []);
  //     }
  //   };
  //   fetchRestaurantByDay();
  //   console.log(`restaurant: ${restaurants}`);
  //   console.log(apiRestaurants);
  // }, [selectedDay, request]);
  useEffect(() => {
    const fetchRestaurantByDay = async () => {
      if (selectedDay) {
        request(api.get, `/restaurants/day/${encodeURIComponent(selectedDay)}/`);
        typeof apiRestaurants === "array"
          ? setRestaurants(apiRestaurants)
          : setRestaurants([]);
        setRestaurants(apiRestaurants);

      }
    };
    fetchRestaurantByDay();
  }, [selectedDay]);

  // Restaurants map function
  const restaurantsMap = restaurants?.map((restaurant) => {
    return (
      <div>
        <h2>Restaurants</h2>
        {restaurants?.length > 0 ? (
          <ul>
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
          </ul>
        ) : (
          <p>No restaurants available for the selected day</p>
        )}
      </div>
    );
  });

  if (!selectedDay) {
    return <div>Please select a day to see available restaurants</div>;
  } else if (loading) {
    return <div>Loading...</div>;
  } else if (error) {
    return <div>Error: {error.message}</div>;
  } else {
    return <>{restaurantsMap}</>;
  }
}
