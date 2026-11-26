// GA4 website measurement and playbook download events.
const measurementId = 'G-1VYWZ9S5HD';
if (/^G-[A-Z0-9]+$/.test(measurementId)) {
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.appendChild(tag);
  document.querySelectorAll('.download').forEach(link => {
    link.addEventListener('click', () => {
      window.gtag('event', 'playbook_download', {
        resource_name: 'Short_Hold_Acquisition_Playbook',
        link_url: link.href
      });
    });
  });
}
