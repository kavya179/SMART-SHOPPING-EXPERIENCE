import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollToTop component:
 * 1. Resets scroll position to (0, 0) immediately upon any route/search/key change.
 * 2. Intercepts navigation clicks to guarantee the viewport scrolls to top.
 */
function ScrollToTop() {
  const location = useLocation();

  useEffect(() => {
    // Reset window scroll
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'instant',
    });

    // Reset standard scrollable containers if any
    const appMain = document.querySelector('.app-main');
    if (appMain) {
      appMain.scrollTop = 0;
    }
    const appContainer = document.querySelector('.App');
    if (appContainer) {
      appContainer.scrollTop = 0;
    }
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, [location.pathname, location.search, location.key]);

  useEffect(() => {
    const handleLinkClick = (e) => {
      const link = e.target.closest('a');
      if (link) {
        const href = link.getAttribute('href');
        // Only scroll to top for internal site links, not anchor jumps like #section
        if (href && (href.startsWith('/') || href === '')) {
          window.scrollTo({
            top: 0,
            left: 0,
            behavior: 'instant',
          });
        }
      }
    };

    document.addEventListener('click', handleLinkClick);
    return () => {
      document.removeEventListener('click', handleLinkClick);
    };
  }, []);

  return null;
}

export default ScrollToTop;
