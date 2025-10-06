"""
Volume Scoring Module - Scoring and grading system for volume analysis
"""

import numpy as np

# Normal range constants
NORMAL_MIN = -30  # dBFS
NORMAL_MAX = -10  # dBFS
OPTIMAL_RANGE = (-25, -15)  # Best range for clear speech


def calculate_volume_score(result: dict) -> dict:
    """
    Calculate comprehensive score and grade for volume analysis.

    Args:
        result (dict): Volume analysis result with frame_values, min, max, avg, etc.

    Returns:
        dict: Enhanced result with score, grade, and comparison data
    """
    # Get basic metrics
    volume_min = result["volume_min"]
    volume_max = result["volume_max"]
    volume_avg = result["volume_avg"]
    coverage_percent = result["coverage_vs_target"]

    # Calculate individual component scores (0-100)

    # 1. Coverage Score (40%) - How much time in normal range
    coverage_score = min(100, coverage_percent * 1.2)  # Boost coverage importance

    # 2. Average Position Score (30%) - How close avg is to optimal range
    if OPTIMAL_RANGE[0] <= volume_avg <= OPTIMAL_RANGE[1]:
        avg_score = 100
    elif NORMAL_MIN <= volume_avg <= NORMAL_MAX:
        # Score based on distance from optimal center
        optimal_center = (OPTIMAL_RANGE[0] + OPTIMAL_RANGE[1]) / 2
        distance = abs(volume_avg - optimal_center)
        max_distance = max(abs(NORMAL_MIN - optimal_center), abs(NORMAL_MAX - optimal_center))
        avg_score = max(70, 100 - (distance / max_distance) * 30)
    else:
        # Outside normal range - penalty based on how far
        if volume_avg < NORMAL_MIN:
            # Too quiet
            distance = NORMAL_MIN - volume_avg
            avg_score = max(0, 70 - distance * 2)
        else:
            # Too loud
            distance = volume_avg - NORMAL_MAX
            avg_score = max(0, 70 - distance * 2)

    # 3. Range Control Score (20%) - Consistent volume
    volume_range = result["volume_range"]
    if volume_range <= 15:  # Very consistent
        range_score = 100
    elif volume_range <= 25:  # Good consistency
        range_score = 85
    elif volume_range <= 35:  # Acceptable
        range_score = 70
    else:  # Too much variation
        range_score = max(0, 70 - (volume_range - 35) * 2)

    # 4. Boundary Score (10%) - Avoid extremes
    boundary_score = 100
    if volume_min < -50:  # Too quiet moments
        boundary_score -= (abs(volume_min) - 50) * 2
    if volume_max > -5:   # Risk of clipping
        boundary_score -= (abs(volume_max) - 5) * 3
    boundary_score = max(0, boundary_score)

    # Calculate weighted total score
    total_score = (
        coverage_score * 0.4 +
        avg_score * 0.3 +
        range_score * 0.2 +
        boundary_score * 0.1
    )

    # Determine grade
    if total_score >= 90:
        grade = "A+ Xuất sắc"
        status = "🟢"
    elif total_score >= 80:
        grade = "A Tốt"
        status = "🟢"
    elif total_score >= 70:
        grade = "B+ Khá tốt"
        status = "🟡"
    elif total_score >= 60:
        grade = "B Trung bình khá"
        status = "🟡"
    elif total_score >= 50:
        grade = "C+ Cần cải thiện"
        status = "🟠"
    elif total_score >= 40:
        grade = "C Yếu"
        status = "🟠"
    else:
        grade = "D Rất yếu"
        status = "🔴"

    # Check if in normal range
    in_normal_range = NORMAL_MIN <= volume_avg <= NORMAL_MAX

    # Generate friendly recommendations focusing on volume levels
    recommendations = []

    # Analyze volume level patterns
    if volume_avg < -35:
        if coverage_percent < 40:
            recommendations.append("🔊 Bạn có xu hướng nói với **âm thanh nhỏ** và thường xuyên ở mức âm thấp. Hãy thử điều chỉnh để đưa âm thanh lên **mức trung bình** - điều này sẽ giúp người nghe dễ chịu hơn!")
        else:
            recommendations.append("🎯 Âm thanh của bạn ở **mức nhỏ** nhưng khá ổn định. Thử nâng lên **mức trung bình** để tăng độ rõ ràng khi giao tiếp.")
    elif volume_avg > -8:
        recommendations.append("⚠️ Bạn có xu hướng nói với **âm thanh lớn**, có thể gây khó chịu cho người nghe. Hãy thử điều chỉnh xuống **mức trung bình** để tạo sự thoải mái.")
    elif OPTIMAL_RANGE[0] <= volume_avg <= OPTIMAL_RANGE[1]:
        recommendations.append("🌟 Tuyệt vời! Âm thanh của bạn ở **mức trung bình tối ưu** và rất dễ nghe. Hãy duy trì mức âm thanh này!")
    elif NORMAL_MIN <= volume_avg <= NORMAL_MAX:
        recommendations.append("👍 Âm thanh của bạn ở **mức trung bình**, khá phù hợp cho giao tiếp tự nhiên.")

    if coverage_percent < 50:
        recommendations.append("📈 Bạn nên tập luyện duy trì **âm thanh ở mức ổn định** trong vùng trung bình để tăng độ rõ ràng.")
    elif coverage_percent < 70:
        recommendations.append("💪 Bạn đã khá ổn trong việc duy trì **mức âm thanh phù hợp**! Hãy tiếp tục luyện tập.")

    if volume_range > 35:
        recommendations.append("🎚️ **Mức âm thanh** của bạn biến động từ nhỏ đến lớn khá nhiều. Thử tập giữ **âm thanh ổn định** ở một mức để tạo cảm giác thoải mái.")
    elif volume_range > 25:
        recommendations.append("🔄 **Âm thanh** của bạn có chút biến động giữa các mức. Hãy chú ý giữ **mức âm đều đặn** trong suốt quá trình nói.")

    if not recommendations:
        recommendations.append("🏆 Xuất sắc! **Mức âm thanh** của bạn ở **mức trung bình chuẩn**, ổn định và rất dễ nghe. Hãy tiếp tục duy trì!")

    # Add scoring details to result
    enhanced_result = result.copy()
    enhanced_result.update({
        "score": round(total_score, 1),
        "grade": grade,
        "status": status,
        "in_normal_range": in_normal_range,
        "score_breakdown": {
            "coverage_score": round(coverage_score, 1),
            "avg_score": round(avg_score, 1),
            "range_score": round(range_score, 1),
            "boundary_score": round(boundary_score, 1)
        },
        "recommendations": recommendations,
        "comparison": {
            "normal_min": NORMAL_MIN,
            "normal_max": NORMAL_MAX,
            "optimal_min": OPTIMAL_RANGE[0],
            "optimal_max": OPTIMAL_RANGE[1],
            "user_vs_normal": "Âm thanh mức trung bình" if in_normal_range else ("Âm thanh mức nhỏ" if volume_avg < NORMAL_MIN else "Âm thanh mức lớn")
        }
    })

    return enhanced_result


def create_results_table_data(results_per_file: list, file_labels: list) -> list:
    """
    Create comprehensive table data for multiple files with scoring.

    Args:
        results_per_file (list): List of volume analysis results
        file_labels (list): List of filenames

    Returns:
        list: List of dictionaries for table display
    """
    table_data = []

    for i, (result, filename) in enumerate(zip(results_per_file, file_labels)):
        # Calculate score for this file
        scored_result = calculate_volume_score(result)

        table_data.append({
            "STT": i + 1,
            "Tên file": filename,
            "Min (dBFS)": f"{scored_result['volume_min']:.1f}",
            "Max (dBFS)": f"{scored_result['volume_max']:.1f}",
            "Avg (dBFS)": f"{scored_result['volume_avg']:.1f}",
            "Range (dB)": f"{scored_result['volume_range']:.1f}",
            "Coverage (%)": f"{scored_result['coverage_vs_target']:.1f}%",
            "Điểm": f"{scored_result['score']:.1f}",
            "Xếp loại": scored_result['grade'],
            "Trạng thái": scored_result['status'],
            "So với chuẩn": scored_result['comparison']['user_vs_normal']
        })

    return table_data