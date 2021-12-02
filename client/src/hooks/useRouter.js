import { useMemo } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import queryString from "query-string";
// Hook
export default function useRouter() {
  const params = useParams();
  const location = useLocation();
  const history = useNavigate();
  // Return our custom router object
  // Memoize so that a new object is only returned if something changes
  return useMemo(() => {
    return {
      // For convenience add push(), replace(), pathname at top level
      push: history,
      pathname: location.pathname,
      // Merge params and parsed query string into single "query" object
      // so that they can be used interchangeably.
      // Example: /:topic?sort=popular -> { topic: "react", sort: "popular" }
      query: {
        ...queryString.parse(location.search), // Convert string to object
        ...params,
      },
      // Include match, location, history objects so we have
      // access to extra React Router functionality if needed.
      location,
      history,
    };
  }, [params, location, history]);
}
