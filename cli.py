
from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from matplotlib.patches import Rectangle
import pandas as pd
import plotly.graph_objects as go

from .utils import (
    read_raw, stretch_to_uint8, load_yaml, load_catalog, load_tracking,
    parse_local_timestamp_from_filename, nearest_tracking_row, star_altaz,
    affine_from_leds, transform_point, sky_offset_to_pixel, pix_per_arcmin
)

def build_parser():
    p = argparse.ArgumentParser(prog='focal-plane-overlay')
    p.add_argument('raw_image')
    p.add_argument('--catalog', required=True)
    p.add_argument('--tracking', default=None, help='Skycam/tracking CSV. Required unless --ignore-skycam is used.')
    p.add_argument('--config', required=True)
    p.add_argument('--source-id', type=int, default=38)
    p.add_argument('--led-threshold', type=float, default=150.0)
    p.add_argument('--led-search-radius', type=float, default=70.0)
    p.add_argument('--alpha-deg', type=float, default=0.0, help='Extra rotation of image-sky axes')
    p.add_argument('--offset-el-arcmin', type=float, default=None, help='Deliberate commanded elevation offset in arcmin')
    p.add_argument('--offset-east-arcmin', type=float, default=None, help='Deliberate commanded east offset in arcmin')
    p.add_argument('--ignore-skycam', action='store_true', help='Ignore skycam/tracking RA/Dec. Use the catalog star centroid and LED-derived camera center to compute the pointing offset.')
    p.add_argument('--output', required=True)
    p.add_argument('--zoom-output', default=None, help='Optional second output image zoomed on the camera-center/star offset vector.')
    p.add_argument('--zoom-halfwidth', type=float, default=120.0, help='Half-width in pixels for --zoom-output view.')
    p.add_argument('--vmin', type=float, default=50.0, help='vmin')
    p.add_argument(
        '--interactive-output',
        default=None,
        help='Optional interactive Plotly HTML output for inspecting x, y, z and overlays.'
    )

    #Added 6/22/26 for calibration square 
    p.add_argument('--calibration-output', default=None,
               help='Squared calibration image')
    p.add_argument('--calibration-vmax', type=float, default=40.0,
               help='vmax for calibration image')
    p.add_argument('--calibration-zoom-halfwidth', type=float, default=240.0, help='Half-width in pixels for --calibration')
    
    return p



def pixel_to_sky_offset(delta_pix, alpha_deg, pix_per_arcmin):
    """Invert sky_offset_to_pixel().

    sky_offset_to_pixel() uses
        pixel_delta = R(alpha) @ [-delta_el, -delta_east] * pix_per_arcmin
    so this returns (delta_east_arcmin, delta_el_arcmin).
    """
    a = np.deg2rad(alpha_deg)
    R_inv = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    base = R_inv @ (np.asarray(delta_pix, dtype=float) / pix_per_arcmin)
    delta_el_arcmin = -base[0]
    delta_east_arcmin = -base[1]
    return float(delta_east_arcmin), float(delta_el_arcmin)


def save_interactive_plotly(
    image,
    cat,
    src,
    leds_found,
    cam_center,
    star_xy,
    offset_start_xy,
    offset_end_xy,
    offset_label,
    output_html,
    vmin=0,
    vmax=255,
):
    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=image,
        colorscale='gray',
        zmin=vmin,
        zmax=vmax,
        name='image',
        hovertemplate='x=%{x}<br>y=%{y}<br>z=%{z}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=cat['X_IMAGE'],
        y=cat['Y_IMAGE'],
        mode='markers+text',
        text=cat['ID'].astype(str),
        textposition='top center',
        marker=dict(size=10, color='red', symbol='circle-open', line=dict(width=2)),
        name='catalog sources',
        hovertemplate=(
            'ID=%{text}<br>'
            'x=%{x:.2f}<br>'
            'y=%{y:.2f}<extra></extra>'
        ),
    ))

    fig.add_trace(go.Scatter(
        x=leds_found[:, 0],
        y=leds_found[:, 1],
        mode='markers+text',
        text=[f'L{i+1}' for i in range(len(leds_found))],
        textposition='top center',
        marker=dict(size=14, color='cyan', symbol='circle-open', line=dict(width=3)),
        name='LEDs',
        hovertemplate='LED %{text}<br>x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=[cam_center[0]],
        y=[cam_center[1]],
        mode='markers+text',
        text=['center'],
        textposition='top right',
        marker=dict(size=16, color='lime', symbol='cross'),
        name='camera center',
        hovertemplate='camera center<br>x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=[star_xy[0]],
        y=[star_xy[1]],
        mode='markers+text',
        text=[f"star ID {int(src['ID'])}"],
        textposition='top right',
        marker=dict(size=16, color='yellow', symbol='x'),
        name='selected star',
        hovertemplate='selected star<br>x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=[offset_start_xy[0], offset_end_xy[0]],
        y=[offset_start_xy[1], offset_end_xy[1]],
        mode='lines+markers',
        line=dict(color='magenta', width=4),
        marker=dict(size=8, color='magenta'),
        name='offset vector',
        hovertemplate='x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>',
    ))

    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref='paper',
        yref='paper',
        text=offset_label.replace('\n', '<br>'),
        showarrow=False,
        align='left',
        bgcolor='rgba(0,0,0,0.65)',
        font=dict(color='white'),
    )

    fig.update_yaxes(autorange='reversed', scaleanchor='x')
    fig.update_xaxes(constrain='domain')

    fig.update_layout(
        title='Interactive focal-plane overlay',
        width=1400,
        height=950,
        dragmode='pan',
        hovermode='closest',
    )

    fig.write_html(output_html, include_plotlyjs='cdn')
    print(f'Saved interactive {output_html}')




def main():
    args = build_parser().parse_args()
    cfg = load_yaml(args.config)
    cal, site, target, optics = cfg['calibration'], cfg['site'], cfg['target'], cfg['optics']
    pointing = cfg.get('pointing', {})

    image = read_raw(args.raw_image)
    cat = load_catalog(args.catalog)

    use_skycam = not args.ignore_skycam
    row = None
    utc_dt = None
    star_az = star_el = ctr_az = ctr_el = None

    if use_skycam:
        if args.tracking is None:
            raise ValueError('--tracking is required unless --ignore-skycam is used')
        track = load_tracking(args.tracking)
        utc_dt = parse_local_timestamp_from_filename(args.raw_image, cfg.get('timing', {}).get('local_to_utc_hours', 7.0))
        row = nearest_tracking_row(track, utc_dt)

        # true star sky position
        star_az, star_el = star_altaz(
            float(target['ra_deg']), float(target['dec_deg']), utc_dt,
            float(site['lat_deg']), float(site['lon_deg']), float(site['height_m'])
        )
        # tracking/boresight center sky position
        ctr_az, ctr_el = star_altaz(
            float(row['trackingRA']), float(row['trackingDec']), row['Timestamp'].to_pydatetime(),
            float(site['lat_deg']), float(site['lon_deg']), float(site['height_m'])
        )

    master_leds = np.array(cal['led_coordinates'], dtype=float)
    mirror_center = np.array(cal['mirror_center'], dtype=float)
    offset = np.array(cal.get('offset', [0.0, 0.0]), dtype=float)
    M, leds_found = affine_from_leds(master_leds, image, args.led_threshold, args.led_search_radius)
    cam_center = transform_point(M, mirror_center + offset)

    ##EDITING DONE HERE - O.K.

    half_size = 80  # pixels

    # Define Region of Interest bounds around mirror center defined in overlay_config
    xmin = cam_center[0] - half_size
    xmax = cam_center[0] + half_size
    ymin = cam_center[1] - half_size
    ymax = cam_center[1] + half_size

    roi = cat[
    (cat['X_IMAGE'] >= xmin) & (cat['X_IMAGE'] <= xmax) &
    (cat['Y_IMAGE'] >= ymin) & (cat['Y_IMAGE'] <= ymax)
    ]   
    if len(roi) == 0:
        raise ValueError("No catalog sources found inside ROI")


    roi = roi.copy()
    roi['area'] = roi['A_IMAGE'] * roi['B_IMAGE']
    #src = roi.loc[roi['FLUX_ISO'].idxmax()] #picks brightest centroid (with most flux)
    src = roi.loc[roi['area'].idxmax()] #picks largest area centroid

    star_xy = np.array([
    float(src['X_IMAGE']),
    float(src['Y_IMAGE'])
    ], dtype=float)
    #print(cat.columns)
    print(f"Auto-selected source ID: {int(src['ID'])}")

    #src = cat.loc[cat['ID'] == args.source_id].iloc[0]
    #star_xy = np.array([float(src['X_IMAGE']), float(src['Y_IMAGE'])], dtype=float)

    ##EDITING OVER; 5/29/26

    ppm = pix_per_arcmin(float(optics['pix2mm']), float(optics['mm_per_arcmin']))

    # commanded offset to subtract from expected star-center separation
    offset_el_arcmin = args.offset_el_arcmin if args.offset_el_arcmin is not None else float(pointing.get('offset_el_arcmin', 0.0))
    offset_east_arcmin = args.offset_east_arcmin if args.offset_east_arcmin is not None else float(pointing.get('offset_east_arcmin', 0.0))

    if use_skycam:
        # Star offset relative to tracking center on the sky. This is the old mode:
        # compare the measured catalog star centroid against the expected position
        # predicted from the skycam/tracking center.
        d_east_arcmin_raw = (star_az - ctr_az) * np.cos(np.deg2rad(ctr_el)) * 60.0
        d_el_arcmin_raw = (star_el - ctr_el) * 60.0
        delta_pix_raw = sky_offset_to_pixel(d_east_arcmin_raw, d_el_arcmin_raw, args.alpha_deg, ppm)
        tracking_star_xy = cam_center + delta_pix_raw

        d_east_arcmin_cmd = d_east_arcmin_raw - offset_east_arcmin
        d_el_arcmin_cmd = d_el_arcmin_raw - offset_el_arcmin
        delta_pix_cmd = sky_offset_to_pixel(d_east_arcmin_cmd, d_el_arcmin_cmd, args.alpha_deg, ppm)
        offset_star_xy = cam_center + delta_pix_cmd

        reference_xy = tracking_star_xy
        reference_label = 'track'
        vector_start_xy = offset_star_xy if (abs(offset_el_arcmin) > 0 or abs(offset_east_arcmin) > 0) else tracking_star_xy
        vector_label = 'residual'
    else:
        # No-skycam mode: use only the measured star centroid and the LED-derived
        # camera center. For zero commanded offset, the pointing offset is simply
        # star_xy - cam_center.
        delta_pix_raw = star_xy - cam_center
        d_east_arcmin_raw, d_el_arcmin_raw = pixel_to_sky_offset(delta_pix_raw, args.alpha_deg, ppm)

        # If a deliberate commanded offset is supplied, draw the expected offset
        # position from the camera center and report the residual from there to
        # the measured star centroid.
        delta_pix_cmd_expected = sky_offset_to_pixel(offset_east_arcmin, offset_el_arcmin, args.alpha_deg, ppm)
        offset_star_xy = cam_center + delta_pix_cmd_expected
        d_east_arcmin_cmd, d_el_arcmin_cmd = pixel_to_sky_offset(star_xy - offset_star_xy, args.alpha_deg, ppm)

        tracking_star_xy = cam_center
        reference_xy = cam_center
        reference_label = 'center'
        vector_start_xy = offset_star_xy if (abs(offset_el_arcmin) > 0 or abs(offset_east_arcmin) > 0) else cam_center
        vector_label = 'pointing offset'

    #img8 = stretch_to_uint8(image), default vmin=0, vmax=255
    img8 = image
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.imshow(img8, origin='upper', cmap='gray', vmin=0, vmax=255)

    for i, pt in enumerate(leds_found):
        ax.add_patch(plt.Circle((pt[0], pt[1]), 15, fill=False, color='cyan', lw=2))
        ax.text(pt[0] + 8, pt[1] + 8, f'L{i+1}', color='cyan', fontsize=9)

    ax.plot(cam_center[0], cam_center[1], marker='+', markersize=18, markeredgewidth=2.5, color='lime')
    ax.text(cam_center[0] + 12, cam_center[1] - 12, 'center', color='lime', fontsize=10)

    ell = Ellipse(
        (src['X_IMAGE'], src['Y_IMAGE']),
        width=2 * float(src['A_IMAGE']),
        height=2 * float(src['B_IMAGE']),
        angle=float(src['THETA_IMAGE']),
        fill=False,
        edgecolor='red',
        linewidth=2.0
    )
    ax.add_patch(ell)
    ax.plot(star_xy[0], star_xy[1], marker='x', color='red', markersize=10, mew=2)
    ax.text(star_xy[0] + 12, star_xy[1] - 12, 'star', color='yellow', fontsize=10)

    if use_skycam:
        ax.plot(tracking_star_xy[0], tracking_star_xy[1], marker='+', color='magenta', markersize=18, mew=2.5)
        ax.text(tracking_star_xy[0] + 12, tracking_star_xy[1] + 12, 'track', color='magenta', fontsize=10)

    has_offset = abs(offset_el_arcmin) > 0 or abs(offset_east_arcmin) > 0
    if has_offset:
        ax.plot(offset_star_xy[0], offset_star_xy[1], marker='+', color='orange', markersize=18, mew=2.5)
        ax.text(offset_star_xy[0] + 12, offset_star_xy[1] - 12, 'cmd offset', color='orange', fontsize=10)
        ax.annotate('', xy=(star_xy[0], star_xy[1]), xytext=(offset_star_xy[0], offset_star_xy[1]),
                    arrowprops=dict(arrowstyle='->', lw=2, color='magenta'))
        if use_skycam:
            ax.annotate('', xy=(offset_star_xy[0], offset_star_xy[1]), xytext=(tracking_star_xy[0], tracking_star_xy[1]),
                        arrowprops=dict(arrowstyle='->', lw=1.8, color='magenta', linestyle='dashed'))
        axis_origin = offset_star_xy
    else:
        ax.annotate('', xy=(star_xy[0], star_xy[1]), xytext=(reference_xy[0], reference_xy[1]),
                    arrowprops=dict(arrowstyle='->', lw=2, color='magenta'))
        axis_origin = reference_xy

    # Values used for the offset-vector label and optional zoom panel.
    if has_offset:
        offset_start_xy = offset_star_xy
        offset_end_xy = star_xy
        offset_dx_pix = star_xy[0] - offset_star_xy[0]
        offset_dy_pix = star_xy[1] - offset_star_xy[1]
        offset_deast_arcmin = d_east_arcmin_cmd
        offset_del_arcmin = d_el_arcmin_cmd
        offset_label_title = 'residual offset'
    else:
        offset_start_xy = reference_xy
        offset_end_xy = star_xy
        offset_dx_pix = star_xy[0] - reference_xy[0]
        offset_dy_pix = star_xy[1] - reference_xy[1]
        offset_deast_arcmin = d_east_arcmin_raw
        offset_del_arcmin = d_el_arcmin_raw
        offset_label_title = 'pointing offset'

    offset_mag_pix = float(np.hypot(offset_dx_pix, offset_dy_pix))
    offset_mag_arcmin = float(np.hypot(offset_deast_arcmin, offset_del_arcmin))
    offset_label = (
        f'{offset_label_title}\n'
        f'dx={offset_dx_pix:.1f} pix, dy={offset_dy_pix:.1f} pix\n'
        f'|d|={offset_mag_pix:.1f} pix = {offset_mag_arcmin:.1f} arcmin\n'
        f'dEast={offset_deast_arcmin:.1f} arcmin, dEl={offset_del_arcmin:.1f} arcmin'
    )

    # Put a compact label near the vector in the full-frame image too.
    mid_xy = 0.5 * (offset_start_xy + offset_end_xy)
    ax.text(mid_xy[0] + 15, mid_xy[1] - 15, offset_label,
            color='white', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.65))

    axis_len_arcmin = float(optics.get('axis_length_arcmin', 20.0))
    d_el_pix = sky_offset_to_pixel(0.0, axis_len_arcmin, args.alpha_deg, ppm)
    d_e_pix = sky_offset_to_pixel(axis_len_arcmin, 0.0, args.alpha_deg, ppm)

    ax.annotate('', xy=(axis_origin[0] + d_el_pix[0], axis_origin[1] + d_el_pix[1]), xytext=(axis_origin[0], axis_origin[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
    ax.text(axis_origin[0] + d_el_pix[0] - 25, axis_origin[1] + d_el_pix[1] - 5, '+El', color='orange', fontsize=10)

    ax.annotate('', xy=(axis_origin[0] + d_e_pix[0], axis_origin[1] + d_e_pix[1]), xytext=(axis_origin[0], axis_origin[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='deepskyblue'))
    ax.text(axis_origin[0] + d_e_pix[0] + 5, axis_origin[1] + d_e_pix[1] + 25, '+E', color='deepskyblue', fontsize=10)

    #originally had (ID {args.source_id})
    if use_skycam:
        left_info = (
            f"{target.get('name', 'star')} (ID {int(src['ID'])})\n"
            f"true Az = {star_az:.3f}°\n"
            f"true El = {star_el:.3f}°\n"
            f"star xy = ({star_xy[0]:.1f}, {star_xy[1]:.1f})"
        )
    else:
        left_info = (
            f"{target.get('name', 'star')} (ID {int(src['ID'])})\n"
            f"skycam ignored\n"
            f"star centroid xy = ({star_xy[0]:.1f}, {star_xy[1]:.1f})"
        )
    ax.text(0.02, 0.98, left_info, transform=ax.transAxes, va='top', ha='left',
            color='yellow', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.65))

    if use_skycam:
        right_info = (
            f"center Az = {ctr_az:.3f}°\n"
            f"center El = {ctr_el:.3f}°\n"
            f"pred track xy = ({tracking_star_xy[0]:.1f}, {tracking_star_xy[1]:.1f})\n"
            f"star-center ΔEast = {d_east_arcmin_raw:.1f} arcmin\n"
            f"star-center ΔEl = {d_el_arcmin_raw:.1f} arcmin"
        )
    else:
        right_info = (
            f"pointing offset from centroid-center\n"
            f"Δx = {star_xy[0] - cam_center[0]:.1f} pix\n"
            f"Δy = {star_xy[1] - cam_center[1]:.1f} pix\n"
            f"ΔEast = {d_east_arcmin_raw:.1f} arcmin\n"
            f"ΔEl = {d_el_arcmin_raw:.1f} arcmin"
        )
    ax.text(0.98, 0.98, right_info, transform=ax.transAxes, va='top', ha='right',
            color='magenta', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.65))

    bottom_left = (
        f"camera center = ({cam_center[0]:.1f}, {cam_center[1]:.1f})\n"
        f"alpha = {args.alpha_deg:.1f}°\n"
        f"scale = {ppm:.3f} pix/arcmin"
    )
    ax.text(0.02, 0.02, bottom_left, transform=ax.transAxes, va='bottom', ha='left',
            color='lime', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.65))

    if has_offset:
        bottom_right = (
            f"cmd offset East = {offset_east_arcmin:.1f} arcmin\n"
            f"cmd offset El = {offset_el_arcmin:.1f} arcmin\n"
            f"cmd-corrected xy = ({offset_star_xy[0]:.1f}, {offset_star_xy[1]:.1f})\n"
            f"resid ΔEast = {d_east_arcmin_cmd:.1f} arcmin\n"
            f"resid ΔEl = {d_el_arcmin_cmd:.1f} arcmin"
        )
        ax.text(0.98, 0.02, bottom_right, transform=ax.transAxes, va='bottom', ha='right',
                color='orange', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.65))

    title = 'LEDs, camera center, measured star centroid, and pointing offset' if not use_skycam else 'LEDs, camera center, true star, predicted star position from tracking center, and optional commanded offset'
    ax.set_title(title)
    ax.set_xlabel('x [pix]')
    ax.set_ylabel('y [pix]')
    plt.tight_layout()
    fig.savefig(args.output, dpi=150)
    print(f'Saved {args.output}')

    if args.interactive_output:
        save_interactive_plotly(
            image=img8,
            cat=cat,
            src=src,
            leds_found=np.asarray(leds_found),
            cam_center=cam_center,
            star_xy=star_xy,
            offset_start_xy=offset_start_xy,
            offset_end_xy=offset_end_xy,
            offset_label=offset_label,
            output_html=args.interactive_output,
            vmin=0,
            vmax=255,
        )

    ##default vmin = 0, vmax=255; MESSING WITH LABELING 6/1/25
    if args.zoom_output:
        zhw = float(args.zoom_halfwidth)
        zoom_center = 0.5 * (offset_start_xy + offset_end_xy)
        figz, axz = plt.subplots(figsize=(7, 7))
        axz.imshow(img8, origin='upper', cmap='gray', vmin=0, vmax=255)

        axz.plot(cam_center[0], cam_center[1], marker='+', markersize=18,
                 markeredgewidth=2.5, color='blue') #default color = lime

        axz.text(cam_center[0] + 8, cam_center[1] - 8, 'center',
                 color='lime', fontsize=10)

        ellz = Ellipse(
            (src['X_IMAGE'], src['Y_IMAGE']),
            width=2 * float(src['A_IMAGE']),
            height=2 * float(src['B_IMAGE']),
            angle=float(src['THETA_IMAGE']),
            fill=False,
            edgecolor='red',
            linewidth=2.0
        )
        #"""
        axz.add_patch(ellz)
        axz.plot(star_xy[0], star_xy[1], marker='x', color='red',
                 markersize=10, mew=2)
        axz.text(star_xy[0] + 8, star_xy[1] + 18,
                 f"star ID {int(src['ID'])}", color='yellow', fontsize=10)

        if has_offset:
            axz.plot(offset_star_xy[0], offset_star_xy[1], marker='+',
                     color='orange', markersize=16, mew=2.5)
            axz.text(offset_star_xy[0] + 8, offset_star_xy[1] - 8,
                     'cmd offset', color='orange', fontsize=10)
            

        axz.annotate('', xy=(offset_end_xy[0], offset_end_xy[1]),
                     xytext=(offset_start_xy[0], offset_start_xy[1]),
                     arrowprops=dict(arrowstyle='->', lw=2.5, color='magenta'))

         #Offset label. Put it near the arrow midpoint.
        mid_xy = 0.5 * (offset_start_xy + offset_end_xy)
        axz.text(mid_xy[0] + 12, mid_xy[1] - 12, offset_label,
                 color='white', fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='black', alpha=0.75))

        
        #Small +E/+El axes at the vector start.
        small_axis_arcmin = min(10.0, max(3.0, offset_mag_arcmin))
        d_el_pix_z = sky_offset_to_pixel(0.0, small_axis_arcmin, args.alpha_deg, ppm)
        d_e_pix_z = sky_offset_to_pixel(small_axis_arcmin, 0.0, args.alpha_deg, ppm)
        axz.annotate('', xy=(offset_start_xy[0] + d_el_pix_z[0]*2, offset_start_xy[1] + d_el_pix_z[1]*2),
                     xytext=(offset_start_xy[0], offset_start_xy[1]),
                     arrowprops=dict(arrowstyle='->', lw=1.8, color='orange'))
        axz.text(offset_start_xy[0] + d_el_pix_z[0] *2 - 5, offset_start_xy[1] + d_el_pix_z[1] -2,
                 '+El', color='orange', fontsize=9, fontweight='bold', bbox=dict(     
        facecolor='black',
        alpha=0.6,
        edgecolor='none',
        pad=1.5 ))
        axz.annotate('', xy=(offset_start_xy[0] + d_e_pix_z[0]*2, offset_start_xy[1] + d_e_pix_z[1]*2),
                     xytext=(offset_start_xy[0], offset_start_xy[1]),
                     arrowprops=dict(arrowstyle='->', lw=1.8, color='deepskyblue'))
        axz.text(offset_start_xy[0] + d_e_pix_z[0] - 5, offset_start_xy[1] + d_e_pix_z[1]*2 ,
                 '+East', color='deepskyblue', fontsize=9, fontweight='bold', bbox=dict(
        facecolor='black',
        alpha=0.6,
        edgecolor='none',
        pad=1.5
        
    )) #BELONGS TO FINAL AXZ.TEXT
        #"""

        axz.set_xlim(zoom_center[0] - zhw, zoom_center[0] + zhw)
        axz.set_ylim(zoom_center[1] + zhw, zoom_center[1] - zhw)
        axz.set_xlabel('x [pix]')
        axz.set_ylabel('y [pix]')
        axz.set_title('Zoomed pointing offset')
        plt.tight_layout()
        figz.savefig(args.zoom_output, dpi=180)
        print(f'Saved zoom {args.zoom_output}')

    #Calibration square added 6/22/26
    if args.calibration_output:
        zhw = float(args.calibration_zoom_halfwidth)
        zoom_center = 0.5 * (offset_start_xy + offset_end_xy)
        figz, axz = plt.subplots(figsize=(7, 7))
        axz.imshow(img8, origin='upper', cmap='gray', vmin=0, vmax=args.calibration_vmax)

        axz.plot(cam_center[0], cam_center[1], marker='+', markersize=18,
                 markeredgewidth=2.5, color='blue') #default color = lime
        
        #actual code that draws square
        square_side_length = 126.5
        half_length = square_side_length/2
        square = Rectangle(
            (cam_center[0] - half_length - 5, cam_center[1] - half_length),
            2 * half_length,
            2 * half_length,
            fill=False,
            edgecolor='blue',
            linewidth=1
        )
        axz.add_patch(square)

        axz.text(cam_center[0] + 8, cam_center[1] - 8, 'center',
                 color='lime', fontsize=10)

        ellz = Ellipse(
            (src['X_IMAGE'], src['Y_IMAGE']),
            width=2 * float(src['A_IMAGE']),
            height=2 * float(src['B_IMAGE']),
            angle=float(src['THETA_IMAGE']),
            fill=False,
            edgecolor='red',
            linewidth=2.0
        )

        axz.set_xlim(zoom_center[0] - zhw, zoom_center[0] + zhw)
        axz.set_ylim(zoom_center[1] + zhw, zoom_center[1] - zhw)
        axz.set_xlabel('x [pix]')
        axz.set_ylabel('y [pix]')
        axz.set_title('Zoomed pointing offset')
        plt.tight_layout()
        figz.savefig(args.calibration_output, dpi=180)
        print(f'Saved zoom {args.calibration_output}')    


    if use_skycam:
        print(f'Nearest tracking timestamp: {row["Timestamp"]}')
        print(f'True star AltAz:   Az={star_az:.6f} El={star_el:.6f}')
        print(f'Tracking center:   Az={ctr_az:.6f} El={ctr_el:.6f}')
        print(f'Tracking star xy:  x={tracking_star_xy[0]:.2f} y={tracking_star_xy[1]:.2f}')
        print(f'Offset star xy:    x={offset_star_xy[0]:.2f} y={offset_star_xy[1]:.2f}')
    else:
        print('Skycam/tracking ignored')
        print(f'Camera center xy:  x={cam_center[0]:.2f} y={cam_center[1]:.2f}')
        print(f'Star centroid xy:  x={star_xy[0]:.2f} y={star_xy[1]:.2f}')
        print(f'Pointing offset:   dx={star_xy[0]-cam_center[0]:.2f} pix dy={star_xy[1]-cam_center[1]:.2f} pix')
        print(f'Pointing offset:   dEast={d_east_arcmin_raw:.3f} arcmin dEl={d_el_arcmin_raw:.3f} arcmin')
        if has_offset:
            print(f'Cmd offset xy:     x={offset_star_xy[0]:.2f} y={offset_star_xy[1]:.2f}')
            print(f'Residual offset:   dEast={d_east_arcmin_cmd:.3f} arcmin dEl={d_el_arcmin_cmd:.3f} arcmin')
    print(f'pix_per_arcmin:    {ppm:.6f}')



if __name__ == '__main__':
    main()
